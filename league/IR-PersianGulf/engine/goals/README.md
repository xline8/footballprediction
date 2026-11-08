# G-IRPG goals engine

This is the preregistered goals-only Dixon-Coles engine for the IR
Persian Gulf Pro League. It reads
`league/IR-PersianGulf/data/ir_persiangulf_matches.csv` and writes dev
results under this directory. The three arms are `gate_zero` (the
unmodified reference DC fit), `shrink` (the DE-3Liga `<6 prior matches`
rating shrink), and `x2` (the frozen entrant offset: attack -0.18 and
defence +0.15 for teams with zero matches in the training window). X2 is
applied in `adjusted_lambdas`, uses only Persian Gulf training counts, and
does not use Azadegan data.

Run from the repository root:

    python3 league/IR-PersianGulf/engine/goals/run_g_irpg.py dev

`dev` writes `results_dev.json` and `results_dev.csv`. `virgin-metrics`
reruns dev and reads 2025/2026 only when at least one arm passes the frozen
dev gate; otherwise it writes the no-read sentinel. `virgin-predict --arm`
is explicit and writes the prediction CSV and fitted parameters. Half-time
presentation lines use the frozen 0.427 first-half share in every column.

The virgin commands are deliberately not run as part of the preregistered
dev-only execution.
