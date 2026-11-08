# Data understanding — IS-BestaDeildin

The source is the FotMob world warehouse, league id 215, with one row per
finished match. The corpus is 942 matches: 2021 has 132 regular matches and
2022–2026 have 162 each (132 regular, 15 championship, 15 relegation).

The era map is the central constraint. 2021–2022 contain goals and events but
no stats, period splits or referee names. 2023 has stats for 162/162, splits
for 90/162 and referees for 81/162. 2024 has 162/162 stats and splits and
126/162 referees; 2025 has 162/162 and 130/162; virgin 2026 has 162/162 and
65/162 referees. No payload contains xG and all 942 shotmaps are empty.

Calendar seasons are carried as `2021` through `2026`. The `phase` field is
regular/championship/relegation. Split rows are included, not discarded, and
the no-playoff condition is preserved. Machine-readable inventory and EDA are
in `inventory_summary.json` and `eda_summary.json`.
