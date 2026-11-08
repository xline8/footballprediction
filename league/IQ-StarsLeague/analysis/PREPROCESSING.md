# Step 2 — Preprocessing

The builder reads the FotMob-524 index and payloads, retains only rows with a numeric final score, and writes one row per played match plus two team rows per match. It asserts all 2,032 payloads have null stats, empty shotmaps, null lineups, and empty referee text. The 49 scoreless schedule placeholders are excluded; they are not 0–0 matches.

`phase=playoff` is assigned when `general.matchRound` is exactly `1/2` or `final`; all other played matches are `regular`. The three 2023/2024 playoff rows are excluded from all model training and evaluation. Team state keys on FotMob team id, never display name.

Where events exist, first-half goals are counted from event order before the explicit `Half` event with `halfStrKey=halftime_short`. This is stoppage-time safe. Matches without events receive null first-half fields; nothing is imputed. Red-card fields are likewise null without events and count `Red` plus `YellowRed` events when events exist.

The 2024/2025 fixture anomaly is retained as played: Karbalaa–Erbil occurred in rounds 16, 25, and 31 (2025-01-23, 2025-03-30, 2025-05-02), while Al Kahrabaa–Erbil occurred once. No match is dropped and no missing fixture is fabricated. CSVs are generated locally and ignored by git; `build_data.py` is the reproducible artefact.
