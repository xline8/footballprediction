# Pre-registration — G-DE3 goals model

Frozen 2026-11-09 before fitting. Goals-only Dixon–Coles; no xG blend exists. Half-life, damping, smoothing, home advantage, rho grid, and score matrix follow the DE-2 reference. Gate Zero is the reference; SHRINK applies the frozen <6 prior-match rating shrink. X2 is not adopted. Dev is season-blocked 2022/2023–2024/2025 after a 2021/2022 seed; virgin is 2025/2026 read once; 2026/2027 is not read. All rows are regular phase.

## Gate

Goals dev — beat climatology on 1X2 LL AND RPS AND league base rate on OU2.5 LL else FAIL (variants moot). Virgin read ONCE, dev-passing arms only: PASS if LL ≤ best baseline AND |calibration error| ≤ 1pp; PROVISIONAL PASS if ≤ 1 SE; else FAIL. Calibration = actual − predicted. If no arm passes dev, virgin NOT read. Ties go to Gate Zero.

Primary market: OU2.5; 1X2 LL/RPS are co-primary gate metrics. No model fitting is performed in this phase.
