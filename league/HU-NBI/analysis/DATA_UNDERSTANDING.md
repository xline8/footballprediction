# HU-NBI data understanding

The source is the FotMob world warehouse, league id 212. The builder reads the index and payload path, keys fixtures by the two FotMob team ids, and writes one row per played match. The complete seasons each contain 198 matches; the in-progress 2026/2027 season contains 77 and is reserved.

| season | matches | teams | matches/team | stats | events | named referee | periods | shotmap | hasPlayoff |
|---|---:|---:|---|---:|---:|---:|---|---:|---|
| 2021/2022 | 198 | 12 | 33 each | 198 | 198 | 130 | All | 0 | absent (198) |
| 2022/2023 | 198 | 12 | 33 each | 198 | 198 | 168 | All | 0 | absent (198) |
| 2023/2024 | 198 | 12 | 33 each | 193 | 198 | 178 | All | 0 | absent (198) |
| 2024/2025 | 198 | 12 | 33 each | 197 | 198 | 167 | All | 0 | false (124), absent (74) |
| 2025/2026 | 198 | 12 | 33 each | 198 | 198 | 18 | All | 0 | false (198) |
| 2026/2027 | 77 | 12 | 12 or 13 | 77 | 77 | 31 | All | 0 | false (77) |

Format verification is structural, not assumed: every complete season has 12 ids and 33 appearances per id, exactly 12×33/2 = 198 matches. No payload has a playoff flag set to true, and no separate playoff/table phase was found. The current season has the expected partial count and unequal appearance counts because it is unfinished.

The complete stat-key inventory is identical wherever a stats block exists: `BallPossesion`, `total_shots`, `ShotsOnTarget`, and `corners`, all under `Periods.All` → `top_stats`. There are no other sections or period splits. `big_chance`, `touches_opp_box`, `fouls`, `yellow_cards`, `red_cards`, and every xG key occur zero times. There are no shotmap shots in any of the 1,067 payloads.

Per-season inventory (the count is the number of payloads carrying that key) is therefore: 2021/22 — BallPossesion/total_shots/ShotsOnTarget/corners 198 each; 2022/23 — 198 each; 2023/24 — 193 each; 2024/25 — 197 each; 2025/26 — 198 each; 2026/27 — 77 each. Every season has only section `top_stats` and period `All`.

The six no-stats matches are 2023/2024: 4206645, 4206646, 4206637, 4206643, 4206644; and 2024/2025: 4512451. They remain in the CSV with `has_stats=0` and null stat fields; scores, events, and derived event fields are retained.

Names are not stable identifiers. The observed id/name table is:

| id | observed names |
|---:|---|
| 132717 | Kecskemeti TE |
| 1602 | Vasas Budapest |
| 1667 | Zalaegerszeg |
| 187020 | Mezokovesd SE |
| 2035 | Nyiregyhaza Spartacus FC; Nyíregyháza Spartacus FC |
| 2280 | Kazincbarcikai BSC |
| 2476 | Diosgyori VTK |
| 355346 | Puskas FC Academy; Puskás FC Academy |
| 45720 | Gyirmot |
| 465382 | Kisvarda; Kisvárda |
| 5755 | Györi ETO |
| 7778 | MTK Budapest |
| 7779 | Budapest Honved; Kispest Honved; Kispest Honvéd |
| 7986 | Paksi SE |
| 8036 | Fehervar FC; Videoton FC Fehervar |
| 8043 | Ujpest; Újpest |
| 8222 | Ferencvaros; Ferencváros |
| 8369 | Debrecen |

Referee names are carried when the info box has non-empty text. Coverage falls sharply in 2025/2026 (18/198), so the referee feature is not eligible. Event types include goals, cards, substitutions, half markers, and occasional missed penalties. Card values are `Yellow`, `YellowRed`, and `Red`.
