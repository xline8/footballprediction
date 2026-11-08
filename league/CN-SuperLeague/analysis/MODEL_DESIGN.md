# Phase A2 — Model Design: CN-SuperLeague

Feasibility is positive for all five markets in 2023–2026. The fit era is
2023+; no 2021/2022 rows enter a fit. Calibration is **actual − predicted**.
Gate Zero dev failure means candidate FAIL and the virgin is not read.

## Feasibility matrix

| Candidate | Target | Seed / dev / virgin | Primary / ladder | Arms |
|---|---|---|---|---|
| G-CN | goals | 2023 / 2024–25 / 2026 | OU 2.5 | Gate Zero, SHRINK |
| S-CN | total SOT | 2023 / 2024–25 / 2026 | 9.5 / 8.5, 9.5, 10.5 | Gate Zero, RS |
| C-CN | total corners | 2023 / 2024–25 / 2026 | 9.5 / 8.5, 9.5, 10.5 | Gate Zero, X7 |
| K-CN | stats-feed total yellows | 2023 / 2024–25 / 2026 | 3.5 / 3.5, 4.5 | Gate Zero only |
| T-CN | total shots | 2023 / 2024–25 / 2026 | 26.5 / 25.5, 26.5, 27.5 | A, B, E9 |

Stats dev has n=480 and virgin n=240. Goals uses the 2023 season as seed;
stats markets warm up on 2023. All 2023+ seasons are ordinary rows with a
phase flag. Halves are presentation splits using the constants in config.

## G-CN — goals

Reference the production Dixon–Coles pattern: goals-only observations,
season-blocked expanding fit, half-life 270, and its established dependence
handling. Gate Zero is that production pattern. SHRINK is the sanctioned
thin-data arm: when a team has fewer than six prior in-league matches, scale
its attack and defence effects by n/6. X2 is dropped as a feature, but its
descriptive mover evidence motivates this arm.

## S-CN — shots on target

Gate Zero is the v5 pattern with its constants copied verbatim from the
SOT preregistration: trailing target-rate ensemble, rating observations, and
the frozen count distribution. RS is the same architecture with the
Beta–Binomial prior changed from 200 to 20,000. The target is the stats-feed
home-plus-away SOT total; X5 supplies the trailing reference component.

## C-CN — corners

Gate Zero is the production `corners_v3` pattern, including X9 possession and
big-chance territorial covariates. X7 is the same construction with
`touches_opp_box` as the territorial covariate, using the TH/J1 C prereg
wording. If the eight-match coverage rule is not met for a fixture, X7 is
inactive and Gate Zero supplies the prediction.

## K-CN — cards

Gate Zero only, following the TH K precedent. The target is frozen
stats-feed `yellow_cards` home plus away. The event-unified count is reported
only as a sensitivity, and referee strictness is not used because of its
weak reliability and virgin coverage failure. X5 remains the cards reference
architecture despite its weak yellow reliability.

## T-CN — total shots

Mirror `PREREG_T_TH.md` / the T-J1 shots family exactly, changing only the
league, windows, line, and frozen CN level.

* **Arm A (v1 pattern):** rating regression for team shots for/against,
  negative-binomial total with arm-specific size, ensembled 50/50 with the
  naive trailing-10 member. Fit state, naive state, and updates are strictly
  walk-forward.
* **Arm B (v2 level layer):** Arm A plus the decayed actual/predicted total
  ratio, shrunk to the frozen CN dev mean and clipped to the preregistered
  factor bounds. Tune only the level-layer half-life on the seed.
* **Arm E9:** Arm A with negative-binomial size r re-estimated from the
  trailing-r window, with the preregistered prior and window mechanics.

No fourth arm or post-hoc tuning is permitted.

## Gate legs (frozen)

Dev gate — pooled dev LL at the primary line beats both baselines (league
base rate and naive trailing-10), else arm dead, no virgin read. Virgin legs
— (i) LL at the primary line is no worse than the reference arm and the best
baseline; (ii) calibration absolute breach ≤1 percentage point clean, with
≤1 standard error provisional; (iii) per-season sign check. Among both-pass
arms, the lower virgin LL ships; one pass ships; none FAIL. Calibration is
actual − predicted. For T-CN, the variant per-season check requires the
variant dev LL to beat or tie the reference in at least one of the two dev
seasons. If Gate Zero fails dev, the candidate fails and virgin is not read.
