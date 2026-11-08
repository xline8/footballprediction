# S-USLL1 shots-on-target engine

Production `model_sot.py` v5 port (NB r = 79.94 frozen). Only
`phase == "regular"` rows with the stats feed are used. Arms: `GZ`,
`RS` (Beta-Binomial ratio prior 200 -> 20,000). Warm-up 2021, scored
dev 2022-2024 (n=486), virgin 2025 (n=210, coordinator-gated).
Primary line 8.5; halves presentation via the frozen 0.465 share.

Run: `python3 run_s_usl.py dev` / `virgin-metrics` / `virgin-predict --arm X`.
