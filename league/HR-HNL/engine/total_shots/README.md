# T-HR total-shots engine

Seeded from the programme shots family (CY T engine): joint home/away
log-linear Poisson ratings store (ridge lambda tuned on the warm-up
season, HL = 365, lazy refit 7 days) ensembled 50/50 with naive
trailing-10 through NB over-probabilities. Arms: A (v1), B (v2 level
layer, centre M_BAR = 24.10 — this league's frozen dev-era mean),
C (E9 trailing-200-match NB size). Adaptations vs the seed: primary
line 23.5 (ladder 22.5 / 23.5 / 24.5), HR windows, calibration sign
convention predicted − actual (PREREG_T_HR), and an explicit guard —
arm A dev failure ⇒ virgin NOT read.

Reads `data/hr_matches.csv`. Warm-up 2021/2022; dev scored
2022/2023–2024/2025 (n = 540); virgin 2025/2026 (n = 180).
Run: `python run_t_hr.py dev` then `python run_t_hr.py virgin`.
Predictions (on PASS) carry exp_shots_1h/2h via the frozen 0.4661
constant, presentation only.
