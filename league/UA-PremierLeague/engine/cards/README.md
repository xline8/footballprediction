# K-UA engine (cards)

Production `model_cards.py` pattern (`model.py`: decayed team yellow
ratings + NB count distribution + naive trailing-10 ensemble; NB size
r estimated from warm-up predictions). Gate Zero only (referee X8 not
built: reliability ≈ 0 and virgin referee coverage 48.75%). Target is
the frozen stats-feed yellow total; the virgin run also reports the
preregistered event-feed-target sensitivity (not a gate leg). Era
2023+; warm-up 2023, dev scored 2024+2025 (n=480), virgin 2026 (n=240).
Primary line 3.5.

Run from this directory:
- `python3 run_k_ua.py dev` → results_dev.json + predictions_dev.csv
- `python3 run_k_ua.py virgin` → results_virgin.json + predictions_virgin.csv
  (+ predictions/k_ua_virgin_predictions.csv + fitted_params_virgin.json
  on PASS); refused unless Gate Zero passed dev.
