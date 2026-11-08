# T-SAFD total-shots engine

Reads only `data/safd_matches.csv`, filtering `phase=regular` and
`awarded=0`. The first 90 2025/2026 matches are the frozen tuning block;
the remaining 214 are the dev gate pool. Virgin scoring is conditional
on the recorded dev gate and uses the 94-match transitional 2026/2027
window, continuing the state.

```sh
python3 engine/total_shots/run_t_safd.py dev
python3 engine/total_shots/run_t_safd.py virgin-metrics
python3 engine/total_shots/run_t_safd.py virgin-predict
```

Outputs are `results_dev.json/csv`, `fitted_params.json`,
`results_virgin.json`, `fitted_params_virgin.json`, and predictions only
when an arm passes all frozen legs.
