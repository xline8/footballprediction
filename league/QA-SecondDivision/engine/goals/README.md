# G-QASD goals engine

This is the frozen QA-SecondDivision Dixon–Coles goals port: direct Poisson
log-likelihood, scipy L-BFGS, sum-to-zero ratings, ridge `1e-3`, rho grid
`(0, -0.05, -0.10, -0.15)`, standard Dixon–Coles tau, `MAXG=10`, and home
initialization `0.25`. It has GateZero and ENTRANT arms; ENTRANT applies
`ATT_SHIFT=-0.2391` and reduces defence by `DEF_SHIFT=0.1947` for teams absent
from the immediately preceding season.

The default run is dev-only. From this directory run:

```sh
python3 run_g_qasd.py
```

The dev loader restricts itself to 2024/2025 before fitting, uses rounds 1–7
as a 28-match warm-up and rounds 8–14 as the 28-match scored block. Fits,
climatology, and trailing-10 predictions are expanding and date-grouped:
every match on date D is predicted from history before D, then the whole date
is fed into history. This avoids same-date leakage. Since there is no preceding
season in the corpus for dev, ENTRANT is asserted numerically identical to
GateZero. Outputs are `results_dev.json`, `results_dev.csv`, and
`predictions_dev.csv` in this directory.

Virgin computation is implemented but guarded: set `QASD_RUN_VIRGIN=1` and
do not set `QASD_DEV_ONLY=1`; it is attempted only when GateZero passes the
dev gate. Virgin outputs include `results_virgin.json`,
`fitted_params_virgin.json`, and per-arm `virgin_rows_*.csv` files. The
2026/2027 season is never used by this engine.
