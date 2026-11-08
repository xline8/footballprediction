# Pre-registration — C-KR (K League 1 corners)

Frozen 2026-11-09 before fitting. Reference: production corners_v3.
Dev 2021–2024 (912), virgin 2025 (228 complete), confirmatory 2026 (210
partial, reserved). Primary line OU 8.5; DEV over-rate 0.438.

Arms: Gate Zero with X9 possession/big-chance covariates; X7 box-touch
multiplier arm, active only with the min-8 trailing coverage rule (r for/against
0.846/0.660). Baselines are league base rate at 8.5 and naive trailing-10.

Dev gate: beat base-rate and naive baselines on the frozen count-market
score. Virgin: score no worse than Gate Zero and calibration breach <=1pp
clean PASS, <=1 SE PROVISIONAL PASS, else FAIL. Variants also need the
per-season dev sign check in at least half the seasons. Both-pass chooses the
lower virgin score; ties choose Gate Zero. If Gate Zero fails dev, virgin is
not read. Split rounds >=34 are ordinary matches with phase flag only.
