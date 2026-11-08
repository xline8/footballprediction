# K-TH2 cards engine

Production cards pattern (copied in `model.py`: decayed team yellow
ratings HL=270, prior K=8, NB count distribution, naive trailing-10
ensemble component), Gate Zero only. Target = **event-unified
yellows** (`ev_yellow_home + ev_yellow_away`); the stats feed is null
in every payload for this league, so no stats target exists (see
`../../analysis/DATA_UNDERSTANDING.md`). Referee covariate not used
(X8 dropped: 0% referee coverage in both complete seasons).

Protocol (prereg `prereg/PREREG_K_TH2.md`): regular phase only;
per-match predict-then-update, date-grouped; warm-up = first 90
regular matches of 2024/2025, dev scored n = 182 (one scored-block row
has no event feed and is excluded); virgin = 2025/2026 regular
(n = 306), read once only if the dev gate passes. Primary line 4.5.

Rerun:
```
cd league/TH-ThaiLeague2/engine/cards
python3 run_k_th2.py dev      # writes results_dev.json/csv, predictions_dev.csv
python3 run_k_th2.py virgin   # writes results_virgin.json + predictions_virgin_all.csv;
                              # on PASS also fitted_params_virgin.json and
                              # ../../predictions/k_th2_virgin_predictions.csv
```
Inputs: `../../data/th2_matches.csv`. Halves presentation in the
shipped CSV uses the frozen yellow-cards 1H share 0.3322.
