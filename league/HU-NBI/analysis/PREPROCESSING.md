# HU-NBI preprocessing

`build_data.py` includes every indexed match with a completed score and asserts that the output row count equals the 1,067 league-index rows. It does not fabricate missing stats or halves. The warehouse season labels are preserved verbatim.

Stats are read only from `content.stats.Periods.All`; the values are the home/away pair in the feed. The six rows without a stats block remain usable for goals, cards, referee-independent event fields, and format inventory, but are unavailable to stat-target fits. The target-specific candidate windows therefore use all available target rows; no season is declared unusable because the missingness is only 5/198 or 1/198 in two seasons.

The cards target is event-unified yellows: direct `Yellow` plus `YellowRed`. `YellowRed` contributes one yellow to the target and one to the descriptive red count; `Red` contributes only to red. Plain yellows are present in every season. The stats feed has no cards key anywhere, so an exact stats-versus-events agreement rate is not defined; event-derived cards are selected by construction and reds are excluded.

For event halves, `time <= 45` is first half. This matches the FotMob integer-minute representation in the corpus, including stoppage-time events rendered with minute 45. Goals and cards get event-derived halves; SOT, corners, and total shots are full-time only and their config shares are null.

The 2021/2022 season is warm-up context. Development is expanding walk-forward over 2022/2023, 2023/2024, and 2024/2025. The virgin is 2025/2026, the last complete season. 2026/2027 is reserved and not read by EDA or preregistration calculations.
