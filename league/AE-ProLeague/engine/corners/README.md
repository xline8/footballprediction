# C-AE corners engine
J1-original corners core (ratings + NB, territorial multiplier) — NOT
the TH/CY copy: z_bc here is the trailing big-chance differential (the
TH copy's own-match z_bc leakage defect is absent by construction).
Arms: gate_zero (possession + big-chance multiplier), x7 (box-touch
multiplier). Primary line 10.5; beta tuned at the primary line.
Reads `league/AE-ProLeague/data/ae_matches.csv`; awarded rows excluded.
Dev: `python3 run_c_ae.py dev`. Virgin: `python3 run_c_ae.py virgin
--arms gate_zero x7` (only dev-passing arms; mechanical selection, no
fallback ship). Prereg: PREREG_C_AE.md.
