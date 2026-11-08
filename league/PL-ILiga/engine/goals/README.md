# G-PL-ILiga goals engine

Reads `league/PL-ILiga/data/iliga_matches.csv`; seed is 2021/2022 and dev scores 2022/2023–2024/2025 regular-season matches (918 matches). Arms are Gate Zero and SHRINK. The primary market is OU2.5. Calibration uses actual minus predicted. Run `python3 league/PL-ILiga/engine/goals/run_g_pl_iliga.py dev`.

Only `phase == 'regular'` rows are loaded; the three promotion-playoff rows per complete season are excluded from every fit and gate. The expected-goals columns are empty, so the production DC blend follows its goals-only fallback for every observation.

The dev runner intentionally has no virgin command; virgin evaluation is coordinator-controlled. The copied `virgin()` function retains the PL limitation that its `eligible` check compares an arm's virgin LL only with climatology, not Gate Zero's virgin LL. The preregistered Gate Zero comparison is applied mechanically by the coordinator at verdict time from `results_virgin.json`; `shipped_arm` is not itself the verdict.
