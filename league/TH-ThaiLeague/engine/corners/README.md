# C-TH corners engine

Reads `data/th_matches.csv`; 2022/2023 is the seed and DEV scores 2023/2024–2024/2025 (480 stats rows). Arms are Gate Zero (possession + big chance) and X7 (touches in opponent box); missing X7 history is inactive, never filled. Primary line 9.5, ladder 8.5/9.5/10.5. Outputs are `results_dev.json`, summary CSV, and `predictions_dev.csv`. Run `python3 league/TH-ThaiLeague/engine/corners/run_c_th.py dev`.

DEV only; virgin is forbidden in Phase B.
