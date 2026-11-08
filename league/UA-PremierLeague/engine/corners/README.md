# C-UA engine (corners)

Production `model_corners_v3.py` pattern (`core.py`). Arms: Gate Zero
(X9: trailing possession + big-chance territorial covariates) and X7
(trailing touches_opp_box covariate; where a team's trailing touches
are inactive, the Gate Zero prediction supplies the forecast — prereg
rule, implemented in harness.predict_arm). COORDINATOR CORRECTION:
the TH copy of core.py had silently replaced the trailing territorial
big-chance differential (z_bc) with the target match's OWN big_chance
split — same-match leakage; restored to the J1 original in this build
(see core.py comment). Era 2023+; per-season fits on prior seasons
only; dev scored 2024+2025 (n=480), virgin 2026 (n=240).

Run from this directory:
- `python3 run_c_ua.py dev` → results_dev.json + predictions_dev.csv
- `python3 run_c_ua.py virgin` → results_virgin.json + predictions_virgin.csv
  (+ predictions/c_ua_virgin_predictions.csv + fitted_params_virgin.json
  on PASS); only for arms recorded dev-passing.
