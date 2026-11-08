# C-USLL1 corners engine

Production `model_corners_v3` port. Only `phase == "regular"` rows with
the stats feed are used. Arms: `gate_zero` (X9 possession + big-chance
covariates), `x7` (opp-box-touch multiplier, min-8 trailing rule, Gate
Zero fallback). Scored dev 2022-2024 (n=486), virgin 2025 (n=210,
coordinator-gated). Primary line 9.5; halves via the frozen 0.469 share.

Run: `python3 run_c_usl.py dev` / `virgin --arms gate_zero`.
