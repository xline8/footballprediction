# S-SAFD engine

Inputs: `data/safd_matches.csv`; only regular, non-awarded 2025/2026 and
2026/2027 rows are loaded. `run_s_safd.py dev` writes dev metrics. After a
passing dev gate, `virgin-metrics` evaluates the transitional 2026/2027
window and `virgin-predict` also writes the prediction CSV. Outputs are JSON
and CSV files in this directory; fitted parameters and predictions are under
the league engine's sibling output directories.
