# Phase 1 — Data Understanding: FotMob Germany 3. Liga

The index has 1,992 league_id=208 rows: 342 in 2021/2022, 380 in each complete season 2022/2023–2025/2026, and 130 in the partial 2026/2027. The built table reconciles one-to-one with the index. Stats are present in 1,991/1,992 rows; shotmap is absent in all 1,992. Therefore there is no xG, xGOT, shot-quality, or shotmap feature anywhere in this phase. Virgin is 2025/2026 (380); 2026/2027 is confirmatory only.

## Format and phase

Complete seasons are 20-team double round-robin seasons (380 matches). Every built row is `regular`; the raw corpus contains no 3. Liga promotion/relegation-playoff label. The frozen rule is `Qualification` → `qualification` and exclusion; it never triggers here. No split, playoff group, or points-halving feature is used.

## Coverage

| Season | n | stats | half stats | shotmap | referee | box-touch |
|---|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 342 | 99.7% | 0.6% | 0% | 41.5% | 68.1% |
| 2022/2023 | 380 | 100% | 26.8% | 0% | 98.9% | 64.5% |
| 2023/2024 | 380 | 100% | 96.8% | 0% | 98.4% | 82.6% |
| 2024/2025 | 380 | 100% | 100% | 0% | 92.6% | 100% |
| 2025/2026 | 380 | 100% | 100% | 0% | 88.2% | 100% |
| 2026/2027 partial | 130 | 100% | 93.1% | 0% | 100% | 93.1% |

All target counts are available in the dev seasons and virgin except one missing stats row for SOT, corners, and total shots; those rows remain missing, never imputed. Goals are complete.

## Cards source decision

The stats block is available for 1,963 matches. Stats yellows equal event-derived yellows in only 81.0%; stats are lower in 14.2%, higher in 4.7%, and average −0.178 yellows per match. Adding YellowRed events makes agreement 80.1% and the mean difference −0.277. The design target is therefore event-unified `yellow_home + yellow_away`, with stats yellows retained only for audit.

## Entrants and defects

Entrants from 2. Bundesliga are identifiable by prior-season membership. Arrivals not found in 2. Bundesliga are treated as Regionalliga/up entrants, but that feeder tier is not in the warehouse. The raw entrant deltas versus the league are: 2022/2023 −0.059 GF/+0.057 GA; 2023/2024 +0.015/−0.053; 2024/2025 −0.072/+0.007; virgin 2025/2026 −0.161/+0.291. This is weak and inconsistent, so X2 is not adopted. The only material defects are the shotmap/xG absence, early half-stat absence, early box-touch gaps, and low first-season referee coverage; all are frozen as explicit availability rules.
