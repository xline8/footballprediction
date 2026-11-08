# T-DK1 total-shots engine

Gate Zero: shots-family pattern (model.py ShotsRegressionStore joint
Poisson ridge; lambda tuned on the tuning window by Poisson LL at
25.5, NB r by method of moments — the DK-Superligaen run_t pattern).
X5: trailing-rate blend (0.5*GZ total + 0.5*NaiveTracker total).
X7: box-touch territorial multiplier, beta fitted on prior data over
a BBT-style grid by binary LL at 26.5 (fitted beta was 0.0 on dev, so
X7 was numerically identical to Gate Zero in dev). Seed/tuning
2022/2023, scored dev 2023/2024-2024/2025, virgin 2025/2026. Primary
line 26.5. Runner: run_t_dk1.py dev|virgin.
Prereg: ../../prereg/PREREG_T_DK1.md.
