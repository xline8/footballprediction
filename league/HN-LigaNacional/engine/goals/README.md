# G-HN goals engine

This is the frozen goals-only Dixon–Coles engine for Honduras Liga Nacional. It
uses the two 2021/2022 regular-phase tournaments as seed, then six
tournament-blocked expanding development fits. The 2025/2026 regular phase is
virgin data and 2026/2027 is reserved; neither is read by `dev`.

The arms are Gate Zero and SHRINK. SHRINK scales fitted attack and defence
ratings by prior in-league matches divided by six when a team has fewer than
six matches. The frozen fitter is unchanged: 14 sweeps, damping 0.7, +0.25
smoothing, home advantage initialised at 0.28, `MAXG=10`, production tau,
the frozen rho grid, and 270-day half-life.

Development reports mean 1X2 log loss, RPS, and OU2.5 log loss per tournament
and pooled for the model, pooled-prior climatology, and the reference-only
naive trailing-10 baseline. For each target match, the naive baseline averages
the home team's trailing-10 goals-for with the away team's trailing-10
goals-against (and the analogous away/home components), using at least six
matches per component; otherwise it uses the training-window league mean goals
per team per match. Its probabilities are independent Poissons with no tau or
rho and it never gates.

The dev window is tournament-blocked: each target tournament gets one fit on
all regular-phase rows strictly before its first kickoff. The dev gate is
strict improvement over climatology on pooled 1X2 LL, RPS, and OU2.5 LL.

On a virgin run only, calibration is actual minus mean predicted. A rate is
clean when its absolute difference is at most 1 percentage point. If it is not
clean but the breach is within one standard error of that 1pp boundary, it is
provisional. Both rates must be clean or provisional. A variant also needs to
be no worse than Gate Zero in at least three of six dev tournaments.

Run from this directory:

```text
python3 run_g_hn.py dev
python3 run_g_hn.py virgin
```

`dev` writes `results_dev.json` and `results_dev.csv`, including the SHRINK
audit. `virgin` reruns dev and reads virgin rows only when an arm passes;
the virgin outputs are conditional and are not produced by the dev workflow.
