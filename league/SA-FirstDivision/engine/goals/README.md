# G-SAFD goals engine

This engine implements the frozen Dixon–Coles G-SAFD preregistration for
SA-FirstDivision. It reads only `data/safd_matches.csv`, filtering to the
requested season, `phase == regular`, and `awarded == 0`. Fits use FT goals,
270-day decay, the fixed rho grid, and the two preregistered arms: Gate Zero
and SHRINK.

Outputs are written beside the engine:

- `results_dev.json`, `results_dev.csv`, and `predictions_dev.csv`
- `results_virgin.json` and `fitted_params_virgin.json`
- on a passing virgin verdict, `../../predictions/g_safd_virgin_predictions.csv`

From this directory, rerun with:

```bash
python3 run_g_safd.py dev
python3 run_g_safd.py virgin-metrics
python3 run_g_safd.py virgin-predict
```

Run `dev` first. The virgin commands use the frozen dev artifact; virgin data
is deliberately refused when Gate Zero fails its dev gate. The prediction
file is FT-only and is written only when an arm passes the virgin gates.
