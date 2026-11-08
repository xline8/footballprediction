# Pre-registration — T-KR (K League 1 total shots)

Frozen 2026-11-09 before fitting. Reference: shots-family production
architecture. Dev 2021–2024 (912), virgin 2025 (228 complete), confirmatory
2026 (210 partial, reserved). Primary line OU 23.5; DEV over-rate 0.463.

Arms: v1 Gate Zero; v2 level layer; E9 trailing-r arm. Baselines are league
base rate at 23.5 and naive trailing-10.

Dev gate: beat the base-rate and naive count baselines on the frozen score.
Virgin: score no worse than Gate Zero and calibration breach <=1pp clean PASS,
<=1 SE PROVISIONAL PASS, otherwise FAIL; variants also need the per-season
dev sign check in at least half the seasons. Both-pass selects the lower
virgin score; ties prefer v1/Gate Zero, then v2, then E9. If Gate Zero fails
dev, virgin is not read. Split rounds >=34 are ordinary matches with a phase
flag only; no phase feature.
