# K-COA cards engine

Run from this directory with the project interpreter:

```bash
~/workspace/footballprediction/.venv/bin/python run_k_coa.py dev
~/workspace/footballprediction/.venv/bin/python run_k_coa.py virgin
```

The engine uses event-unified yellows from 2023 onward, a 270-day decayed
venue-split state, prior 8, negative-binomial count probabilities, and the
preregistered Gate Zero and X8 referee arms. Virgin predictions are written
only when the preregistered gates pass.
