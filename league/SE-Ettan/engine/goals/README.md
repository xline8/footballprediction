# goals — Dixon-Coles engine (Gate Zero + SHRINK), see dc.py, arms.py and PREREG_G_SE.md

- Fit: Poisson log-likelihood (scipy L-BFGS, sum-to-zero, ridge 1e-3); rho from grid (0, −0.05, −0.10, −0.15) by training LL; MAXG = 10; tau = standard Dixon-Coles. Fitted rho = 0.0 in all three scored-season fits (2022/2023/2024); home advantage 0.482 / 0.351 / 0.332.
- Dev finding (2026-11-10): SHRINK is numerically identical to GateZero on dev — every team with n < 6 prior in-league matches in a scored season's training set has n = 0 (a pure entrant, already at the league-mean fallback under both arms); every team present in training has n ≥ 9 (2022), ≥ 14 (2023/2024). Verified by an explicit count check and by a synthetic test proving the SHRINK scaling itself is active and distinct when a team has 1–5 prior matches.
- Arms: GateZero (unmodified); SHRINK (FI definition verbatim: at prediction time, team with n < 6 prior in-league matches in the training data has a *= n/6, d *= n/6; n ≥ 6 no change; n = 0 → exponents 0.0). NO ENTRANT arm (X2 rejected, EDA F4).
- Dev: warm-up 2021 (partial, 262 played), scored 2022–2024 (n = 1,440), season-blocked expanding fit. Baselines: climatology + naive trailing-10.
- Dev filter: harness reads ONLY `season_start <= 2024` from `data/se_matches.csv`. It raises (fails loudly) if any row with `season_start > 2024` survives the filter, or if the frozen per-season played counts (2021: 262; 2022/2023/2024: 480 each) do not match. Virgin 2025 and reserve 2026 are never read — there is no virgin code path in this engine at all (Phase 5 owns it).
- Run: `python3 run_g_se.py` from this directory. Outputs: `results_dev.json`, `results_dev.csv`, `fitted_params_dev.json`.
- Environment: numpy 1.26.4, scipy 1.11.4, pandas 2.1.4; no sklearn in this VM (none needed — numpy/scipy only, as foreseen in MODEL_DESIGN.md).

## Divergences from the QA template (outbox-muse2/QA-QatarStars/engine/goals/)

1. **SHRINK instead of ENTRANT.** QA's arms are Gate Zero + ENTRANT; QA's `arms.py`/`dc.py` do not define SHRINK, so the FI definition (verbatim in PREREG_G_SE) is implemented here: `match_counts()` counts matches per team in the whole expanding-fit training set, `shrink_factor()` = min(1, n/6), applied to both attack and defence exponents of both teams in `season_rows()` via the existing `predict_matrix(..., ah, dh, aa, da)` override mechanism. No other code path changes.
2. **Naive trailing-10 league-mean fallback.** QA initialised the fallback once from the warm-up season only. PREREG_G_SE says "the training league mean team goals/match", so the fallback is recomputed per scored season from that season's full training set (`league_mean_goals(train)`). The warm-up 2021 feed still seeds the trailing-10 history before scored 2022.
3. **No virgin code.** QA's `run_goals` contains a gated virgin block; this engine is dev-only by construction — `run_goals` returns `"virgin": None` and contains no code that can read season 2025. Virgin evaluation is a Phase 5 artifact, written separately.
4. **Hard dev guards.** `load_dev_data()` asserts the filter (max season_start ≤ 2024), the frozen per-season counts, all-finished dev rows, and no missing goals. Any breach raises instead of silently proceeding.
5. **Fitted params per scored season** are saved to `fitted_params_dev.json` (QA saved virgin params only).
6. **results_dev.csv** carries a `season` column in addition to QA's columns.
7. **Data layout.** SE seasons are calendar years (`season_start` = season year, e.g. 2022), not split-season strings as in QA; the awarded 2024 match 4398485 (official score 0-3) is kept as the official result in the CSV, exactly as the prereg requires. Two groups (Norra/Södra) with no cross-group matches; no group term fitted.
