# T-LV engine

Inputs are the LV Virsliga stats-era rows in `data/lv_virsliga_matches.csv`. Outputs are `results_dev.json`, `predictions_dev.csv`, and fitted parameters; virgin metrics are written by `python run_t_lv.py virgin --arm A B C` (dev-passing arms only) and the shipped arm's predictions by `python run_t_lv.py virgin-predict --arm <arm>`. Run `python run_t_lv.py dev` from this directory. The frozen 1H/2H presentation constant is 0.4685; it is applied to FT predictions only.
