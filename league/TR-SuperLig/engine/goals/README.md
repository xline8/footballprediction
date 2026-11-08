# G-TR goals engine

Run from the repository root with the project interpreter:

```bash
~/workspace/footballprediction/.venv/bin/python league/TR-SuperLig/engine/goals/run_g_tr.py dev
~/workspace/footballprediction/.venv/bin/python league/TR-SuperLig/engine/goals/run_g_tr.py virgin-metrics
~/workspace/footballprediction/.venv/bin/python league/TR-SuperLig/engine/goals/run_g_tr.py virgin-predict --arm gate_zero
```

`dev` writes walk-forward results. `virgin-metrics` evaluates all three arms on 2025/2026. `virgin-predict` writes the selected arm's predictions and fitted parameters.
