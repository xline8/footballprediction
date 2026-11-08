# Step 2 — Preprocessing

`data/build_data.py` regenerates `ve_matches.csv` and `ve_team_matches.csv` from the relative warehouse index. Only `finished == True` rows are included; the team file has two rows per match.

The frozen phase rule is: playoff iff `matchRound` contains (case-insensitive) `quadrangular` or `final`, OR `general.leagueName` contains `Second stage`, `Second Stage`, `Super Final`, `Final Stage`, or `Fase Final`; otherwise `regular`. It produces 252/51, 240/37, 210/13, 182/52, 182/51, and 182/45 regular/playoff rows for 2021–2026. Bare 2026 rounds 1–13 before July are Apertura regular; later labelled rounds are Clausura.

Final goals come from `header.status.scoreStr`. First-half goals come from non-shootout Goal events at `time <= 45`. The two awarded matches use score-based full-match goals and have `ht_source=none` with missing half goals. No half values, xG, shotmap values, or absent stats are fabricated.

Team names are canonicalized to the most-common observed spelling per FotMob team id. Stats columns are copied from `Periods.All`, `FirstHalf`, and `SecondHalf`; `yellow_cards` from stats is the K target. Event yellow/unified-yellow/red columns remain audit artifacts only. `events_complete` requires both Half and Substitution markers.

The stats era is handled as missing outside the observed payloads. Period-split analyses use only rows with both first- and second-half period blocks. The 2025 feed has two tiers: 55 stats matches carry only 'Top stats' (possession, total shots, SOT, corners), so yellows/fouls/reds/passes exist only in the 288 full-feed matches — the K target is missing (not zero) outside them. The event-card feed is never used for the K target or reliability checks. CSVs and JSON/PNG outputs are regenerable artifacts, not preregistration or model-design documents.
