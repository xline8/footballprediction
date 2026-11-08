# G-AM goals engine

This engine reads only `../data/am_matches.csv`, identifies teams by numeric team ID, and excludes all awarded matches from fits, baselines, and scoring. No playoff matches exist in this league.

Run development evaluation with:

```bash
python3 league/AM-PremierLeague/engine/goals/run_g_am.py dev
```

This writes `results_dev.json` and the per-match `results_dev.csv`. Development loads only 2021/2022 through 2025/2026, seeds on 2021/2022, excludes 7 awarded matches, and scores 653 regular-season matches across the next four seasons. The pooled climatology is the pooled score of each season's expanding prior-season baseline predictions.

Virgin evaluation is run only after the development JSON is frozen:

```bash
python3 league/AM-PremierLeague/engine/goals/run_g_am.py virgin
```

Frozen constants are production half-life `270` days, `14` DC sweeps, damping `0.7`, smoothing `0.25`, and AM presentation half split `0.4335` / `0.5665`. The SHRINK arm applies to all four attack/defence components at prediction time when a team's prior training count is below 6: each component is multiplied by `n/6`; `n=0` remains the Gate Zero league mean.

The dev gate requires both pooled 1X2 LL and RPS, and OU2.5 LL, to beat the expanding climatology. Virgin legs compare LL with Gate Zero and climatology, check calibration using predicted-minus-actual differences, and apply the frozen two-of-four variant sign check. The shipped arm is the lower pooled virgin 1X2 LL among fully passing arms, with Gate Zero winning ties; if none passes, predictions use a labelled Gate Zero fallback.
