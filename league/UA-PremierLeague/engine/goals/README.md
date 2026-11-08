# G-UA engine (goals)

Dixon-Coles goals model, copied pattern from production `model_v2.py`
(`dc.py`), arms in `arms.py` (Gate Zero; SHRINK — under the frozen
season-blocked protocol SHRINK is mathematically identical to Gate
Zero, see harness docstring). Goals-only: no xG exists in this corpus.
Era 2023+ only (prereg era restriction); seed 2023, dev scored
2024+2025 (n=480), virgin 2026 (n=240).

Run from this directory:
- `python3 run_g_ua.py dev` → results_dev.json/csv + predictions_dev.csv
- `python3 run_g_ua.py virgin` → results_virgin.json (+ shipped
  predictions + fitted_params_virgin.json on PASS); refuses arms that
  fail the dev gate recomputed from results_dev.json.

Gate (PREREG_G_CN.md): dev requires pooled 1X2 LL AND RPS AND OU2.5 LL
all better than climatology. DEV OUTCOME: Gate Zero fails the OU2.5
leg (0.6866 vs climatology 0.6802) despite winning 1X2/RPS — G-UA is
FAIL, virgin never read.
