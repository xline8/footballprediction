# Phase 1 — Model design: Egypt Premier League

No models are fit in phase 1. Candidates are G-EG, S-EG, C-EG, K-EG, and T-EG. All phases are ordinary rows; no phase feature. Primary lines come from EDA: pooled 2022/2023–2024/2025 lines are SOT 6.5, corners 8.5, shots 22.5, yellows 3.5; pooled 2023/2024–2024/2025 lines are SOT 7.5, corners 8.5, shots 21.5, yellows 3.5.

| Candidate | Target | Arms |
|---|---|---|
| G-EG | goals | Gate Zero + SHRINK |
| S-EG | SOT | Gate Zero + RS |
| C-EG | corners | Gate Zero + X7 |
| K-EG | stats yellows | Gate Zero only (X8 dropped in FEATURES: r=0.290, virgin referee coverage 26.7%) |
| T-EG | total shots | A / B / C |

Goals are season-blocked: seed 2021/2022, scored 2022/2023–2024/2025. Count markets use per-match walk-forward, warm-up 2021/2022, scored 2022/2023–2024/2025. The virgin 2025/2026 is read once only for dev-passers; 2026/2027 is reserved and not read. Halves use the frozen complete-split constants: goals 0.4202, SOT 0.4445, corners 0.4604, total shots 0.4459, stats yellows 0.3609. Gate legs are the program-standard legs as in the SA/TR preregistration pattern.
