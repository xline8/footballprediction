# Model design — Phase A freeze

No models are fitted in Phase A. The common windows are walk-forward, season-blocked development and one virgin season: goals dev uses 2021/2022 as a seed and evaluates 2022/2023–2024/2025; stats markets use only seasons where their target truly exists (SOT, corners, shots: 2022/2023–2024/2025; cards: the same, because 2021/2022 stats cards are absent); virgin is 2025/2026 for every candidate. 2026/2027 is transitional and unread for verdicts. Primary lines are the standard half-line nearest the dev mean: goals OU 2.5, SOT 9.5, corners 9.5, cards 3.5, total shots 26.5.

| Candidate | Gate Zero reference | Frozen variant arms | Status |
|---|---|---|---|
| G-DK1 | production Dixon–Coles goals-only pattern | SHRINK thin-data prior; X2 mover offset | buildable |
| S-DK1 | `model_sot.py` v5 pattern | X5 trailing target rates; X7 only if explicitly applicable | buildable |
| C-DK1 | `model_corners_v3.py` pattern | X5 trailing target rates; X7 box touches | buildable |
| K-DK1 | `model_cards.py` pattern, stats cards | X5 trailing target rates | buildable |
| T-DK1 | total-shots family pattern | X5 trailing target rates; X7 if supported | buildable |

Goals are goals-only: X1 blend and X3 are unavailable. X2 is adopted because the parent-tier corpus supplies 20 observed cross-tier mover team-seasons and 600 prior-tier matches total, but its parameter must be learned without current-season leakage. Referee X8 is dropped. Each candidate has a preregistration; variants are subordinate to Gate Zero and cannot rescue a failed Gate Zero.
