# G-BNAC dev engine

`python run_g_bnac.py --dev` runs the frozen expanding block-blocked goals evaluation. It reads goals only from `bnac_matches.csv`, fits on dates strictly before each scored block, and writes `results_dev.json` and `results_dev.csv`. Gate Zero is the fitted Dixon–Coles model; X2 adds only the preregistered newcomer offsets. This DEV runner has no virgin or prediction path.
