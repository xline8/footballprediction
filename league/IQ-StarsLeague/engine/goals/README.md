# G-IQSL goals engine

Frozen target: full-time goals and 1X2 from regular-phase `home_goals` and
`away_goals`, with Gate Zero and SHRINK arms. The seed is `2021/2022`; the
expanding scored windows are `2022/2023`, `2023/2024`, and `2024/2025`.
The primary total-goals line is OU 2.5. Fit scope for each scored season is
all regular matches dated strictly before that season's first match date.

The half-life is 270 days, the rho grid is `0, -0.05, -0.10, -0.15`, and the
presentation-only first-half share is `0.4323308271` (second half share
`0.5676691729`). The runner is independent of the current working directory:

```text
python3 league/IQ-StarsLeague/engine/goals/run_g_iqsl.py dev
```

The coordinator runs the virgin command only after reviewing frozen dev
results. This phase does not run it.
