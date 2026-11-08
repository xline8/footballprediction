# G-PBM DEV engine

This directory contains the goals-only Dixon-Coles development harness for
Primera B Metropolitana. It reads the 2021–2025 prefix of
`data/pbm_matches.csv` only; block 2021 is warm-up and blocks 2022–2025 are
scored. There are no virgin, prediction, or fitted-parameter outputs.

Run from this directory with:

```bash
/home/hatch/workspace/footballprediction/.venv/bin/python run_g_pbm.py --dev
```

The run writes `results_dev.json` (full tables and mechanical dev-gate
arithmetic) and `results_dev.csv` (flat tables). Gate Zero is the unmodified
goals-only Dixon-Coles model. X2 applies the preregistered newcomer offsets
only to teams present in the target block and absent from the immediately
preceding block. The trailing-10 baseline combines each team's trailing
goals-for and goals-against means into Poisson lambdas, with league-mean
fallback when a team has no history.
