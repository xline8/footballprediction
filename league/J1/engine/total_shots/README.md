# T-J1 total-shots engine

This is the self-contained J1 implementation of the preregistered total-shots model. It uses the jointly fitted home/away Poisson ratings, the trailing-10 naive member, negative-binomial line probabilities, the tuned level layer, and the trailing-r dispersion arm described in [`league/J1/prereg/PREREG_T_J1.md`](../../prereg/PREREG_T_J1.md).

Run the development pass with:

```text
~/workspace/footballprediction/.venv/bin/python league/J1/engine/total_shots/run_t_j1.py dev
```

That writes `results_dev.json`, `results_dev.csv`, and `fitted_params.json` here. It reads only seasons 2021 through 2025 and uses 2021 as warm-up.

After reviewing the recorded gate, run the virgin pass. It carries state through 2021–2026, scores only dev-passing arms plus both baselines, and can export one passing arm:

```text
~/workspace/footballprediction/.venv/bin/python league/J1/engine/total_shots/run_t_j1.py virgin --export-arm A
```

The virgin results are written here and the requested predictions are written to `league/J1/predictions/t_j1_virgin_predictions.csv`. The preregistration is the governing document; this README only describes how to invoke the engine.
