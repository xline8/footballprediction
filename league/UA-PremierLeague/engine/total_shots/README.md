# T-UA engine (total shots)

Shots family as frozen for T-J1 (`model.py` + runner ported from the
TH build with CN seasons/line): Arm A = v1 pattern (ratings + NB +
naive ensemble), Arm B = A + v2 level layer, Arm C = E9 (NB r from a
trailing 200-match window). Tuning (ridge lambda, r_A, level cell) on
the 2023 warm-up season only. Era 2023+; dev scored 2024+2025 (n=480),
virgin 2026 (n=240). Primary line 26.5.

Run from this directory:
- `python3 run_t_ua.py dev` → results_dev.json/csv + predictions_dev.csv
  + fitted_params.json
- `python3 run_t_ua.py virgin` → results_virgin.json + predictions_virgin.csv
  (+ predictions/t_ua_virgin_predictions.csv + fitted_params_virgin.json
  on PASS); refuses arms that did not pass the recorded dev gate.

Coordinator correction: the TH original's shipped-predictions export
also wrote dev-season rows into the virgin file; the CN runner filters
to the virgin season (the originally exported CN file was likewise
trimmed from 720 to the 240 virgin rows, values unchanged).
