# K-CR cards engine

Run from the repository root with the project interpreter (or system python3 — no third-party
dependencies beyond the standard library):

```bash
python3 league/CR-PrimeraDivision/engine/cards/run_k_cr.py dev
python3 league/CR-PrimeraDivision/engine/cards/run_k_cr.py virgin-metrics
python3 league/CR-PrimeraDivision/engine/cards/run_k_cr.py virgin-predict --arm gate_zero
```

`dev` runs one chronological online pass over 2023/2024 regular: Apertura is warm-up (r estimation,
never scored), Clausura is scored (n = 132). `virgin-metrics` evaluates the dev-surviving arms on
2024/2025 regular (n = 262). `virgin-predict` writes the selected arm's predictions and fitted
parameters.

Reference: production `model_cards.py`, Gate Zero only (no referee arm — referee identity is absent
in this league, EDA F6). Frozen: HL 270 days, K_PRIOR 8, fallback means 2.15/1.95 (production
constants, bind only in the first warm-up matches). Primary line 4.5, secondary 3.5/5.5. Halves in
predictions use the frozen CR constant 0.379 (presentation only). Prereg:
`league/CR-PrimeraDivision/prereg/PREREG_K_CR.md`.
