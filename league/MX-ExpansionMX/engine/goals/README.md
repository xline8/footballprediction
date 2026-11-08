# G-MXE goals engine

Dixon-Coles (production pattern, goals-only), tournament-blocked
walk-forward. Prereg: `../../prereg/PREREG_G_MXE.md`.

- Inputs: league corpus via `../common_mxe.py` (CSV if present,
  else `data/build_data.py` in-memory rows) — blocks 1–9 for dev,
  block 10 (virgin) only through the gated virgin path.
- Run: `python3 run_g_mxe.py dev` → `results_dev.json` +
  `dev_predictions.csv`; `python3 run_g_mxe.py virgin` → reads the
  dev gate, scores the virgin once for dev-passing arms, writes
  `results_virgin.json`, and on PASS `fitted_params_virgin.json` +
  `../../predictions/g_mxe_virgin_predictions.csv`.
- Arms: gate_zero, shrink (preregistered G-J2-lesson arm).
