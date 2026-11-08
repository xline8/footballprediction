# S-UA engine (shots on target)

Production `model_sot.py` v5 pattern (`model.py`: joint Poisson ridge
regression + total-shots ratings + Beta-Binomial on-target ratio +
50/50 naive trailing-10 ensemble, NB r = 79.94). Arms: GZ (BB prior
200), RS (BB prior 20,000). CN-local `harness.py` implements the
PREREG_S_CN protocol (the TH/RU harness carried another league's
primary line in its virgin calibration aliases and was not reused).
Team keys are FotMob ids (CSL clubs rename; name keying would split
histories). Era 2023+; warm-up 2023, dev scored 2024+2025 (n=480),
virgin 2026 (n=240).

Run from this directory:
- `python3 run_s_ua.py dev` → results_dev.json + predictions_dev.csv
- `python3 run_s_ua.py virgin` → results_virgin.json + predictions_virgin.csv
  (+ predictions/s_ua_virgin_predictions.csv + fitted_params_virgin.json
  on PASS); only for arms recorded dev-passing.
