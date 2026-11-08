# NO-OBOSLigaen data understanding

The builder reads FotMob league 203 and freezes 1,440 regular-season matches and 2,880 team-match rows for 2021–2026. Every season is a 16-team, 30-round double round-robin; separate promotion/relegation play-offs are absent. Season 2026 is the complete virgin window through 2026-11-08.

## Format

| Season | n | First | Last | Teams |
|---|---:|---|---|---:|
| 2021 | 240 | 2021-05-15 | 2021-11-27 | 16 |
| 2022 | 240 | 2022-04-02 | 2022-10-29 | 16 |
| 2023 | 240 | 2023-04-10 | 2023-11-12 | 16 |
| 2024 | 240 | 2024-04-01 | 2024-11-09 | 16 |
| 2025 | 240 | 2025-03-31 | 2025-11-08 | 16 |
| 2026 | 240 | 2026-04-05 | 2026-11-08 | 16 |

All 1,440 match IDs are unique. Goal events equal `scoreStr` in 1,440/1,440 matches; awarded matches = 0. The score header remains the target of record.

## Coverage matrix

| Season | n | stats block | four stats keys | events | referee | shotmap | awarded | HT from events |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 240 | 149 | 136 | 240 | 0 | 0 | 0 | 240 |
| 2022 | 240 | 240 | 240 | 240 | 239 | 0 | 0 | 240 |
| 2023 | 240 | 240 | 240 | 240 | 240 | 0 | 0 | 240 |
| 2024 | 240 | 240 | 240 | 240 | 238 | 0 | 0 | 240 |
| 2025 | 240 | 239 | 239 | 240 | 235 | 0 | 0 | 240 |
| 2026 | 240 | 240 | 237 | 240 | 229 | 0 | 0 | 240 |

The content feed is All-only: possession, SOT, corners and total shots. There is no xG, shotmap, cards-stat key or period-split target. Event cards are complete. The 2021 index says 149 stats rows, but only 136 contain all four keys; in 2026 all 240 have a block, while 237 have all four keys.

## Integrity and identity

| Check | Result |
|---|---:|
| Rows / unique IDs | 1,440 / 1,440 |
| Goal events == scoreStr | 1,440 / 1,440 |
| Awarded matches | 0 |
| Event Yellow / YellowRed / Red | 4,522 / 73 / 81 |

Team IDs, not display names, are the identity key. Name variants occur across seasons; the corpus has 32 distinct career IDs and 16 IDs per season. Referee coverage is zero in 2021 and partial thereafter. No shotmap rows exist.

## Quirk register

1. **Thin feed.** Targets are complete, but secondary stats are absent in early 2021 and have the 2025/2026 content gaps above.
2. **2021 gap.** The stats block is absent for roughly rounds 1–13, 2021-05-15 through 2021-07-21: 149 blocks versus 136 complete-key rows. The 13-block difference is incomplete content, not missing matches.
3. **Name variants.** Team names change while IDs persist; all joins and mover logic use IDs.
4. **Referees.** Coverage is 0/240, 239/240, 240/240, 238/240, 235/240 and 229/240 by season; 2021 referee content is zero.
5. **2024 stats-feed regime jump.** SOT per season is 8.80, 9.48, 7.40, 11.85, 10.64, 9.77; total shots are 18.0, 18.4, 19.2, 23.9, 21.4, 23.3. The break between 2023 and 2024 is a counting/feed change, not football; S/T designs span both regimes.
6. **Keyless 2026 blocks.** Sogndal–Hødd (match 5105319), Stabæk–Strømsgodset (5105320), and Strømmen–Lyn (5105321), all 2026-11-08, have a stats block without the four keys. This explains 240 blocks versus 237 complete-key rows.
7. **Virgin completeness.** 2026 has 240/240 matches, 16 teams and complete regular-season coverage; the three keyless blocks affect secondary stats only. The virgin read remains descriptive and does not alter the design.

The complete measured output is in [eda_summary.json](eda_summary.json).
