# S-LV engine

Run `python run_s_lv.py dev` from this directory for Gate Zero and RS dev outputs. Virgin (only for dev-passing arms): `python run_s_lv.py virgin --arm GZ` writes metrics; `python run_s_lv.py virgin-predict --arm GZ` additionally writes the shipped arm's predictions. The target is stats-feed total SOT, ladder 8.5/9.5/10.5. Virgin halves presentation uses frozen constant 0.4637 applied to FT predicted means only.
