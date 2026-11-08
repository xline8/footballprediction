# S-COA shots-on-target engine

Reads the CO-PrimeraA CSV with lowercase `shotsontarget_*` fields. Seed is 2021 Apertura plus 2021 Clausura, dev is 2022 Apertura through 2025 Clausura, and complete virgin is 2026 Apertura. Arms are GZ and RS; no shotmap/XG arms are loaded. The halves split uses the frozen SOT constant 0.4862.

```text
~/workspace/footballprediction/.venv/bin/python league/CO-PrimeraA/engine/sot/run_s_coa.py dev
~/workspace/footballprediction/.venv/bin/python league/CO-PrimeraA/engine/sot/run_s_coa.py virgin
```

Results are written here, with virgin predictions at `league/CO-PrimeraA/predictions/s_coa_virgin_predictions.csv` when the frozen gate passes.


