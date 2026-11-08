# S-BRB shots-on-target engine

Reads `league/BR-SerieB/data/brb_matches.csv` and models total shots on target at the frozen 7.5 line. Gate Zero is the frozen v5 model; RS raises the Beta-Binomial prior. Dev uses 2021 warm-up and scores 2022–2024. Virgin is 2025 only, continuing from the dev end state and read once for dev-passing arms.

```text
python3 league/BR-SerieB/engine/sot/run_s_br.py dev
python3 league/BR-SerieB/engine/sot/run_s_br.py virgin-metrics
python3 league/BR-SerieB/engine/sot/run_s_br.py virgin-predict --arm RS
```

Results and virgin fitted parameters are written here. The shipped prediction file is `predictions/s_brb_virgin_predictions.csv`; its 1H/2H columns are presentation-only using the frozen SOT split 0.467/0.533.
