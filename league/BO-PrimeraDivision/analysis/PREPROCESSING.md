# Step 2 — Preprocessing

`data/build_data.py` regenerates `data/bo_matches.csv` and `data/bo_team_matches.csv` from the relative warehouse path in the index. The match CSV has one row per finished match; the team CSV has two rows per match and is the input shape for trailing team features.

Identity is FotMob team ID. The builder uses the most frequent observed spelling per ID and retains the raw variants in its console output. Examples include Nacional Potosi/Potosí, Guabira/Guabirá, Bolivar/Bolívar, Real Potosi/Real Potosí, and GV San Jose/GV San José.

Only numeric `roundName` is `phase=regular`; playoff names `1/4`, `1/2`, and `final` are `phase=playoff`. All fits, scored windows, reliability calculations, and frozen constants use regular rows only. Goals come from the final score. First-half goals come from Goal events with `time <= 45`, so 45+x is treated as first half. Period features are populated only from `Periods.FirstHalf` and `Periods.SecondHalf`; no earlier-season halves are fabricated.

Cards are stored both as stats-feed `yellow_cards` and event-unified `Yellow + YellowRed`; K-BO targets the latter. `events_complete` requires both Half and Substitution markers, with the complementary `events_incomplete` flag. Pre-2025 event feeds carry no Substitution events at all (0/240 in 2021, 0/333 in 2022), so the flag is False for every pre-2025 match by construction and is meaningful only in 2025–2026 (0 incomplete there). Referee empty text is written as `null`. Three 2022 play-off ties carry PenaltyShootout events; play-offs are excluded from every fit, so shootouts never enter a scored window (regular results settle at 90 minutes). CSVs are generated artifacts and are not preregistration or model outputs.
