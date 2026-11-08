# K-USLL1 cards engine

Production `model_cards.py` port. Target: unified yellows from the
STATS feed, only on `cards_target_valid` rows (season >= 2023 with the
yellow_cards key present; the 2021-22 stats feed is broken and the
event feed carries no card events in 2021-2025 - see prereg). Only
`phase == "regular"` rows. NO warm-up: cold start at the 2023 opener;
the NB r per method is estimated on the 2023 scored records (prereg
cold-start reading). Scored dev 2023-2024 (n=313), virgin 2025 (n=210,
coordinator-gated). Primary line 5.5, ladder 4.5/5.5/6.5. Arms:
`gate_zero`, `x8` (referee covariate; missing referee -> Gate Zero, no
imputation). Halves presentation via the frozen 0.373 share.

Run: `python3 run_k_usl.py dev` / `virgin-metrics` / `virgin-predict --arm X`.
