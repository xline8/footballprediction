# K-SAFD engine

Inputs: `data/safd_matches.csv`; only regular, non-awarded 2025/2026 and
2026/2027 rows are loaded. Run `run_k_safd.py dev` for the frozen dev gate.
After a pass, `virgin-metrics` evaluates the transitional window and
`virgin-predict` also writes the prediction CSV. Outputs are JSON and CSV
files in this directory, with fitted parameters and predictions in sibling
output directories.
