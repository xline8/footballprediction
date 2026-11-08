# Step 1 — Data Understanding (RO-LigaII, FotMob id 9113)

Source: `data_enrichment/fotmob_world_index.csv`, filtered to `league_id = 9113`, with the per-match JSONs read from the warehouse path in the index. The full scan contains 1,513 finished matches. The coverage statements below were measured from payloads, not inferred from index flags.

## Inventory

| Season | Matches | Stats present | Shotmap shots | Named referee | Events non-empty | Goal events |
|---|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 264 | 0 | 0 | 0 | 245 | 701 |
| 2022/2023 | 264 | 0 | 0 | 0 | 243 | 653 |
| 2023/2024 | 262 | 0 | 0 | 0 | 236 | 595 |
| 2024/2025 | 264 | 0 | 0 | 0 | 240 | 627 |
| 2025/2026 | 319 | 0 | 0 | 0 | 302 | 864 |
| 2026/2027 | 140 | 0 | 0 | 0 | 134 | 404 |
| **Total** | **1,513** | **0** | **0** | **0** | **1,400** | **3,844** |

Every payload has `header.status.finished = True` and a score. `content.stats` is `None` in all 1,513 payloads; the index `has_stats=False` flag agrees, but this result was verified from the payloads. Shotmap arrays hold zero shots in all 1,513 files. Referee text is blank in all 1,513 files. There is no xG source.

## Format

| Phase | 2021/22–2024/25 | 2025/26 | 2026/27 so far |
|---|---:|---:|---:|
| Liga II regular | 190 | 231 | 140 |
| Promotion Group | 30 | 30 | 0 |
| Relegation Group A | 21 | 28 | 0 |
| Relegation Group B | 21 | 28 | 0 |
| Relegation Playoff | 2 | 2 | 0 |

Regular play is a single round-robin: 20 teams and rounds 1–19 through 2024/2025, then 22 teams and rounds 1–21 in 2025/2026. That 20→22 boundary is a format change. Promotion is six teams over ten rounds. Relegation groups are seven-team single round-robins through 2024/2025 and eight-team groups in 2025/2026. The relegation playoff is a two-legged final, home/away reversed a week apart, against a Liga III side; it is excluded from modelling.

## Feed quirks and audit counts

- Events are non-empty in 1,400/1,513 matches. The 113 empty-event matches are all 0–0 except match `3666264` (2022-02-24: ASU Politehnica Timisoara 0–3 Petrolul Ploiesti), a feed gap with no events.
- Goal events total 3,844 against 3,841 score-derived goals: +4 in 2021/2022, exact in 2022/2023–2024/2025 and 2026/2027, and −1 in 2025/2026.
- There are 2,800 half events. Substitution events exist only in 2021/2022 (606). Card events contain 148 `Red` and 106 `YellowRed`, but zero straight `Yellow` events. Thus yellow is not a recoverable target; red is retained only for audit and is not a model target.

