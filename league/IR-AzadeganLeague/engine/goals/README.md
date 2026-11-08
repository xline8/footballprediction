# G-IRAZ goals engine

This is the preregistered goals-only Dixon-Coles engine for the IR
Azadegan League. It reads
`league/IR-AzadeganLeague/data/ir_azadegan_matches.csv` and writes
dev results under this directory. The two arms are `gate_zero`
(reference DC) and `shrink` (the DE-3Liga `<6 prior matches` rating
shrink). There is deliberately no X2 arm in this league (see the
prereg): entrants perform at the league mean and the brief forbids
inventing a parent-tier prior.

Run from the repository root:

    python3 league/IR-AzadeganLeague/engine/goals/run_g_iraz.py dev

`dev` writes `results_dev.json` and `results_dev.csv`. `virgin-metrics`
reruns dev and reads 2025/2026 only when at least one arm passes the frozen
dev gate; otherwise it writes the no-read sentinel. `virgin-predict --arm`
is explicit and writes the prediction CSV and fitted parameters. Half-time
presentation lines use the frozen 0.415 first-half share in every column.

Implementation note: the Codex run for this engine was blocked by a
sandbox mount failure (`failed to register synthetic bubblewrap mount
target /tmp/.git`) after copying `dc.py` and adapting `arms.py`;
`harness.py` and this README were completed by the coordinator from
the NL-TweedeDivisie pattern, and the dev run below was verified
independently (climatology recomputed from the CSV with fresh code).
