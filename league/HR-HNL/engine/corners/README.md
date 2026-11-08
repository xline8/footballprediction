# C-HR corners engine

Seeded from the C-J1 engine (production `model_corners_v3` pattern):
Gate Zero = full X9 territorial multiplier (possession + big_chance
trailing differentials, min-8-of-last-10 validity, multiplier clamped
[0.70, 1.43]); arm X7 replaces the multiplier with opp-box touches.
Only functional change vs the seed: the beta-fitting line is this
league's frozen primary line 8.5 (ladder 7.5 / 8.5 / 9.5).

Reads `data/hr_matches.csv`. Warm-up 2021/2022; dev scored
2022/2023–2024/2025; virgin 2025/2026 read once for dev-passing arms.
Run: `python run_c_hr.py dev` then `python run_c_hr.py virgin`
(selection is mechanical per PREREG_C_HR; no fallback shipping).
Predictions (on PASS) carry exp_corners_1h/2h via the frozen 0.4793
constant, presentation only.
