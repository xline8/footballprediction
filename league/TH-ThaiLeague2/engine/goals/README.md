# G-TH2 goals engine

Dixon-Coles (production `model_v2.py` pattern, copied in `dc.py`),
goals-only observation (no xG exists in this league). Arms in
`arms.py`: Gate Zero and SHRINK (ratings of teams with <6 prior
in-league matches shrunk a,d *= n/6).

Protocol (prereg `prereg/PREREG_G_TH2.md`): regular phase only;
dev = within-season walk-forward over 2024/2025 (warm-up 90, scored
183, date-grouped expanding fits); virgin = 2025/2026 regular (306),
fit on all 2024/2025 regular matches, read once for dev-passing arms
only (refused if Gate Zero fails dev).

Rerun:
```
cd league/TH-ThaiLeague2/engine/goals
python3 run_g_th2.py dev      # writes results_dev.json/csv, predictions_dev.csv
python3 run_g_th2.py virgin   # writes results_virgin.json; on PASS also
                              # fitted_params_virgin.json and
                              # ../../predictions/g_th2_virgin_predictions.csv
```
Inputs: `../../data/th2_matches.csv` (regenerate with
`../../data/build_data.py`). Halves presentation in the shipped CSV
uses the frozen goals 1H share 0.4249.
