# G-NLTD goals engine

This is the preregistered goals-only Dixon-Coles engine for NL Tweede Divisie.
It reads `data/nl_tweede_matches.csv` and writes dev results under this
directory. The three arms are `gate_zero` (reference DC), `shrink` (the
DE-3Liga `<6 prior matches` rating shrink), and `x2` (below-tier entrant
prior, frozen at GF -0.093 and GA +0.181 in log-ratio form).

Run from the repository root:

    python3 league/NL-TweedeDivisie/engine/goals/run_g_nltd.py dev

`dev` writes `results_dev.json` and `results_dev.csv`. `virgin-metrics`
reruns dev and reads 2025/2026 only when at least one arm passes the frozen
dev gate; otherwise it writes the no-read sentinel. `virgin-predict --arm`
is explicit and writes the prediction CSV and fitted parameters. Half-time
presentation lines use the frozen 0.436 first-half share in every column.
