# Cyprus 1. Division — data understanding

Phase A uses the FotMob world index league id 136 and its local response store. The builder produces `data/cy_matches.csv` and `data/cy_team_matches.csv` with the Bulgarian analogue schema.

The inventory is 1,271 matches: 192 / 268 / 268 / 240 / 240 / 63 by season from 2021/2022 through 2026/2027. Regular counts are 132 / 182 / 182 / 182 / 182 / 63; championship playoffs are 30 in each completed season; relegation playoffs are 30, 56, 56, 28, 28. Phase names map both `1. Division` and `Cyprus League` to regular; the first ten 2024/2025 regular matches retain the old name.

The stats feed has only `BallPossesion`, `ShotsOnTarget`, `corners`, and `total_shots`, all in `All`. It is present in 1,248 payloads; the source `has_stats` flag is true for 1,249 rows, a one-row flag/payload discrepancy. There are no xG, shotmap, big-chance, box-touch, foul, yellow-card, or period-split fields. Referee is empty in all rows. Events are present in 1,268 rows. The event-goal audit identifies match 3940461 (stored score 0–3, two goal events) as the one score/event mismatch.

Cards are event-unified yellows: `Yellow + YellowRed`, with `cards_source=events`. First-half goals and cards use event time <=45; SOT, corners, and total shots are FT-only. Team identity is the 21 distinct team ids; id 468676 has two names, with `Karmiotissa` retained as the latest name in 2026/2027.
