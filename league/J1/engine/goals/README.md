# G-J1 goals engine

Run from the repository root with the project interpreter:

```bash
~/workspace/footballprediction/.venv/bin/python league/J1/engine/goals/run_g_j1.py dev
~/workspace/footballprediction/.venv/bin/python league/J1/engine/goals/run_g_j1.py virgin-metrics
~/workspace/footballprediction/.venv/bin/python league/J1/engine/goals/run_g_j1.py virgin-predict --arm gate_zero
```

`dev` writes walk-forward results. `virgin-metrics` evaluates all three arms on 2026. `virgin-predict` writes the selected arm's predictions and fitted parameters.
