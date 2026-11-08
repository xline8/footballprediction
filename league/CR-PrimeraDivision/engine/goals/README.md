# G-CR goals engine

Run from the repository root with the project interpreter (or system python3 — no third-party
dependencies beyond the standard library):

```bash
python3 league/CR-PrimeraDivision/engine/goals/run_g_cr.py dev
python3 league/CR-PrimeraDivision/engine/goals/run_g_cr.py virgin-metrics
python3 league/CR-PrimeraDivision/engine/goals/run_g_cr.py virgin-predict --arm gate_zero
```

`dev` writes walk-forward results (2022/2023 + 2023/2024 regular seasons, pooled n = 492).
`virgin-metrics` evaluates Gate Zero on 2024/2025 regular (n = 262). `virgin-predict` writes the
selected arm's predictions and fitted parameters.

Reference: production Dixon-Coles (`model_v2.py`), goals-only (no xG in this league). Frozen:
half-life 270 days, rho grid (0.0, −0.05, −0.10, −0.15), 14 sweeps, damping 0.7, +0.25 smoothing.
Halves in predictions use the frozen CR constant 0.460 (presentation only). Prereg:
`league/CR-PrimeraDivision/prereg/PREREG_G_CR.md`.
