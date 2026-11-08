# T-COA total-shots engine

Reads the CO-PrimeraA CSV with total-shots fields, uses A/B/C shots-family arms, line ladder 23.5/24.5/25.5/26.5, frozen M_BAR 25.06, and frozen 1H share 0.4850. Seed is 2021 Apertura plus 2021 Clausura, dev is 2022 Apertura through 2025 Clausura, and virgin is complete 2026 Apertura.

```text
~/workspace/footballprediction/.venv/bin/python league/CO-PrimeraA/engine/total_shots/run_t_coa.py dev
~/workspace/footballprediction/.venv/bin/python league/CO-PrimeraA/engine/total_shots/run_t_coa.py virgin
```

The engine writes dev/virgin results and conditional fitted parameters, plus virgin predictions on PASS.


