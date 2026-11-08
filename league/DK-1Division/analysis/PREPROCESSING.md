# Preprocessing — DK-1Division

`build_data.py` reads the league-85 index, opens every JSON, retains finished non-cancelled matches, and asserts one unique output row per index row. FT goals come from `header.status.scoreStr`; HT goals come from Goal events with time ≤45. Stats are parsed from `content.stats.Periods` by key and period without imputing absent values.

The phase rule is frozen as `regular` for rounds 1–22, `championship` when the round-23+ Tournament name/link says Promotion or Championship Group, and `relegation` when it says Relegation Group. No `playoff` or `other` rows occur. Split rows remain ordinary observations; the phase is a descriptive flag.

Cards are retained as four separate sources: stats-feed `yellow_cards` and `red_cards`, and event-derived Yellow, YellowRed, and Red counts. The frozen target is stats-feed yellow + red where both teams have both stats. Agreement with all event Card records is: 2022/2023 169/192 (88.0%), 2023/2024 174/192 (90.6%), 2024/2025 177/192 (92.2%), 2025/2026 169/192 (88.0%), and 2026/2027 54/83 (65.1%). 2021/2022 has no stats-feed cards; its event counts remain audit-only and the season is not a cards-model development window. Stats wins because it is the structured team-level source and is complete from 2022/2023, while event totals disagree materially, especially in the transitional season.

No shotmap observations exist. Missing stats are missing, never zero. The CSV includes all-period values, first/second-half values where present, event and feed cards, referee, target coverage flags, and team ids/names. No fitting, engine code, or result files are produced in Phase A.
