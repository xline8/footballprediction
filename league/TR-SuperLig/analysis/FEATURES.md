# Phase 1 — feature decisions

This follows the J1 X1–X9 checklist. All accepted features obey strict pre-match, same-league, trailing-window causality; missing windows are NaN and the relevant arm is inactive.

| feature | decision | TR evidence / implementation |
|---|---|---|
| X1 xG blend | ADOPTED | Goals all seasons; stats xG from 2022/2023 onward. 2021/2022 is an explicit goals-only fallback. |
| X2 cross-tier offset | DROPPED | Single tier; no cross-tier transitions. Promoted/thin-team shrinkage is the goals SHRINK arm instead. |
| X3 set-play xG share | ADOPTED as candidate | xG exists from 2022/2023; pooled split-half ratio reliability 0.401, with season values in eda_numbers.json. Arm is inactive before xG exists. |
| X4 xG/shot | ADOPTED as candidate | Pooled ratio reliability 0.436; shotmap coverage is 100% from 2022/2023. Arm is era/window guarded. |
| X5 trailing target means | ADOPTED | SOT, corners, and unified stats yellows are complete in the played CSV; target-specific missing-window rules remain. |
| X6 xGOT/shot | DROPPED from candidates | Population is only 33.5–40.9% before 2024/2025 and reliability is 0.292 even in the near-universal era; retain the measurement and era guard for future work. |
| X7 box touches | ADOPTED as candidate | For/against reliabilities 0.877/0.775 pooled; coverage is lower early (70.6–89.2%) and the min-window rule handles it. |
| X8 referee yellows | ADOPTED as candidate | Strictness reliability 0.505 pooled / 30 referees; coverage is 50% in 2021/2022, 100% in 2022/2023–2024/2025, 91.5% in 2025/2026, so missing appointments fall back to Gate Zero. |
| X9 territorial covariates | ADOPTED | Production-style possession and big-chance covariates are present; pooled reliabilities are 0.895 and 0.805. |

The measured season-by-season reliabilities, coverage, and era guards are frozen in eda_numbers.json. First-half shares are not eligible features: their true variance is approximately noise. No standings, h2h, attendance, lineup, formation, coach, red-card, game-state, or momentum feature is eligible.

## Consumption map

G-TR uses X1, SHRINK, and X3 where available. S-TR uses X5, RS ratio-shrink, and X4. C-TR uses X5, X9 Gate Zero, and X7. K-TR uses X5 and X8. T-TR uses its three preregistered reference patterns and no new covariate.
