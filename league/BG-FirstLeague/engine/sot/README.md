# S-ZA shots-on-target engine

Reads `data/za_matches.csv`. Production `model_sot.py` v5 pattern.
Warm-up 2022/2023 updates state, never scored; DEV scores
2023/2024–2024/2025 (448 stats rows). Primary line 6.5, ladder
5.5/6.5/7.5. Arms are Gate Zero (GZ) and RS (Beta-Binomial prior
P 200 → 20,000). Calibration uses actual minus predicted. Outputs are
`results_dev.json`, summary CSV, and `predictions_dev.csv`; on a dev
pass, `results_virgin.json` and the shipped predictions CSV.
Run `python3 league/ZA-PSL/engine/sot/run_s_za.py dev`.
