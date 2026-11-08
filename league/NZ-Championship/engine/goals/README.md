# NZ-Championship goals engine — Phase B

This is the development-only G-NZ Dixon–Coles engine. Run from this directory:

```sh
python3 run_g_nz.py dev
```

The harness uses season-blocked expanding fits: each target season is scored
after a fit on matches strictly before that season's first match. It reads the
shared match CSV, retains finals at their 90-minute score, and preserves phase
in the per-match output. The loader guards against loading later-season rows.

`dc.py` is the goals-only reference fit: 14 sweeps, damping 0.7, +0.25
smoothing, initial h=0.28, rho grid `(0.0, -0.05, -0.10, -0.15)`, 270-day
decay, and MAXG=10. No xG keys are present, so the goals-only path is used.

Gate Zero uses fitted ratings unchanged. SHRINK multiplies each fitted attack
and defence rating by `min(1, training_window_match_count / 6)`, with counts
from the fit window. The expected diagnostic is that Miramar Rangers is the
only team below six training-window matches (five in 2022), and it plays no
development-season match, so SHRINK is expected to be bit-identical to Gate
Zero across development. This is an expectation to be confirmed by the
lambda diagnostic.

`results_dev.csv` contains one row per scored development match per arm.
`results_dev.json` contains per-season and pooled model/climatology metrics,
the frozen 0.75 OU2.5 base-rate baseline, the sign check, lambda diagnostics,
and the mechanical gate fields. `results_virgin.json` is only a not-read
marker written by the dev runner.

The mechanical dev gate requires pooled 1X2 log loss and RPS to beat expanding
climatology, and pooled OU2.5 log loss to beat the frozen 0.75 base-rate
baseline. The output reports the numbers and lets that arithmetic determine
the reading; no verdict is pre-written here.
