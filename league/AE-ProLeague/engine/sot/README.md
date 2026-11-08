# S-AE SOT engine
Production model_sot v5 port (ridge Poisson ratings + NB r=79.94 +
Beta-Binomial ratio, 50/50 naive trailing-10 ensemble), arms GZ + RS
(ratio prior 200 -> 20,000). Primary line 9.5.
Reads `league/AE-ProLeague/data/ae_matches.csv`; awarded rows excluded.
Dev: `python3 run_s_ae.py dev`. Virgin: `python3 run_s_ae.py virgin`
(refuses if Gate Zero failed dev). Prereg: PREREG_S_AE.md.
