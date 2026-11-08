# G-BO goals engine

Reads `league/BO-PrimeraDivision/data/bo_matches.csv`. All observations are
goals-only; no xG or shotmap exists in this league. Seed is 2021 regular
(n=240); dev scores 2022–2024 regular (n=896), season-blocked walk-forward;
virgin is 2025 regular (n=240), confirmatory 2026 reserved. Arms are
`gate_zero` (production Dixon-Coles, hl=270) and `shrink` (ratings shrunk by
prior in-league match count / 6 for teams with fewer than 6 prior matches;
vacuous in this design — every team has 0 or 30+ priors at each block start,
so SHRINK ties Gate Zero exactly).

Run from this directory:

```text
python3 run_g_bo.py dev
python3 run_g_bo.py virgin
```

Dev result: Gate Zero FAILS the dev gate (pooled OU2.5 LL 0.698485 vs
climatology 0.693243; 1X2 LL and RPS beat climatology). The virgin command
refuses to read 2025 and writes a FAIL `results_virgin.json`. Authority:
`league/BO-PrimeraDivision/prereg/PREREG_G_BO.md`.
