# NL Eerste Divisie — preprocessing rules

## Inclusion and phase

- Include finished matches selected by FotMob league id 111 and the exact league-name guard `Eerste Divisie`.
- Keep the regular phase represented by the feed: rounds 1–38 in complete seasons. No play-off rows exist in the warehouse, so there is no fabricated exclusion count.
- The 2026/2027 partial season is reserved confirmatory data. Its levels are included in descriptive EDA only; it is never used for fitting or arm selection in this phase.
- Goals are full-time header scores. Half-time goals are reconstructed from goal events when available.

## Stat and split sources

Use the FotMob `content.stats.Periods.All` values for SOT, corners, total shots, possession, big chances, cards cross-checks, and other count targets. Use `FirstHalf`/`SecondHalf` blocks only where present. The half-share constants are measured on the split era (2023/2024 onward), except goals, which are measured from events across all seasons.

The builder keeps xG and shotmap columns even though xG is unavailable and only one shotmap row is non-empty. No imputation turns those missing observations into xG evidence.

## Early cards target check

The check compares all-match stats-feed yellow cards with event-unified cards where `type == Card` and `card == Yellow`; YellowRed and Red are not yellows. `stats_yellow_*` and `event_yellow_*` remain in the match table, while the target columns `yellow_*` use the selected event source.

| season | usable matches | mismatch rate | stats yellows | event yellows |
|---|---:|---:|---:|---:|
| 2021/2022 | 380 | 9.74% | 946 | 1,030 |
| 2022/2023 | 380 | 11.84% | 1,172 | 1,249 |
| 2023/2024 | 380 | 7.89% | 1,221 | 1,242 |
| 2024/2025 | 380 | 10.26% | 1,259 | 1,287 |
| 2025/2026 | 380 | 16.58% | 1,286 | 1,246 |
| 2026/2027 | 139 | 5.76% | 454 | 458 |

The pooled mismatch rate is 222/2,039 = 10.89%; stats total 6,338 versus event total 6,512. The event-unified Yellow-only source is therefore adopted: it is explicit, auditable, and avoids relying on a stats field that disagrees materially and undercounts in five of six seasonal totals. The 2025/2026 reversal is retained as a documented cross-check, not silently discarded.

All future trailing features obey strict pre-kickoff causality, trailing windows, ratio-of-sums construction, and NaN/inactive behavior when coverage is insufficient.
