# KR3 goals engine

This is the preregistered goals-only Dixon–Coles engine for K League 3
(`FotMob 9537`, slug `KR-KLeague3`). It reads regular-phase rows from
`data/kr3_matches.csv`. The dev run loads only seasons 2021–2024: 2021 is
the seed and 2022–2024 are the scored dev seasons. The virgin mode exists
for a later brief, but the virgin season was not read or scored here.

The two arms are:

- `gate_zero`: unmodified DC, with rho grid `{0, -0.05, -0.10, -0.15}`,
  270-day half-life, 14 IPF iterations, and prior 0.25.
- `shrink`: Gate Zero with each team’s attack/defence log-ratings scaled by
  prior K3 match count / 6 when that count is below 6.

The expanding climatology baseline uses all prior seasons before each target
season. A dev pass requires every arm’s pooled 1X2 log loss, pooled RPS, and
pooled OU 2.5 log loss to beat climatology. SHRINK also requires its pooled
seasonal 1X2 log loss to be no worse than Gate Zero in at least 2 of the 3
scored seasons. Gate Zero must pass all three pooled legs; if it fails, the
virgin must not be read.

`results_dev.json` contains pooled and per-season metrics for Gate Zero,
SHRINK, and climatology, plus each gate leg and the SHRINK sign check.
`predictions_dev.csv` has one row per scored match per model arm, with
`match_id, season, date, home, away`, 1X2 probabilities, OU 2.5 over
probability, actual outcome, and actual over indicator (plus fitted lambdas
and rho). Probabilities are normalized by the DC score matrix. The frozen
halves presentation share is `HALF_1H = 0.4273`.

Run the dev walk-forward with:

```bash
python3 league/KR-KLeague3/engine/goals/run_g_kr3.py dev
```

The later virgin entry point is:

```bash
python3 league/KR-KLeague3/engine/goals/run_g_kr3.py virgin
```

It was not run for this brief, and no 2025 or 2026 number is reported here.
