# K-MXE cards engine

Production cards pattern (decayed venue-split ratings, HL=270,
K=8, NB total), Gate Zero only — no referee arm (X8 dropped:
0% referee coverage in dev). Prereg: `../../prereg/PREREG_K_MXE.md`.

- Inputs: clean-era corpus via `../common_mxe.py` (blocks from
  2023/2024 - Apertura; 2022/2023 - Clausura excluded for partial
  yellow capture). Target: unified event yellows (Yellow+YellowRed).
- Run: `python3 run_k_mxe.py dev` → `results_dev.json` (warm-up
  2023/2024 - Apertura unscored + r estimation; scored blocks
  2023/2024 - Clausura … 2025/2026 - Apertura, n=420, primary line
  5.5); `python3 run_k_mxe.py virgin` → only if the dev gate
  passes; on PASS `fitted_params_virgin.json` +
  `../../predictions/k_mxe_virgin_predictions.csv`.
