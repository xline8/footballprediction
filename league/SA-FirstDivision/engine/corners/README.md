# C-SAFD corners engine

Reads only `data/safd_matches.csv`, filtering `phase=regular` and
`awarded=0`. The dev command uses the 2025/2026 first 90 matches as a
never-scored warm-up and scores the remaining 214 by date-grouped
predict-then-update walk-forward fitting. `virgin-metrics` reads the
2026/2027 transitional 94-match window only for dev-passing arms;
`virgin-predict` writes the prediction CSV only when a PASS ships.

```sh
python3 engine/corners/run_c_safd.py dev
python3 engine/corners/run_c_safd.py virgin-metrics
python3 engine/corners/run_c_safd.py virgin-predict
```

Outputs are `results_dev.json/csv`, `results_virgin.json`,
`fitted_params_virgin.json`, and (on PASS) the SAFD predictions CSV.
