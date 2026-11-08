# Phase 1 — Data understanding: Türkiye Süper Lig

All figures are generated from the FotMob world index (`league_id=71`) and
the built CSV. The builder excludes every finished row whose
`header.status.awarded` is true because those are never-played administrative
results.

## Integrity and format

The warehouse contains 1,849 indexed rows and 1,818 played rows. Built rows
are unique by match id. This is one tier, regular double round-robin football;
there are no playoffs or split phases. Team identity is FotMob `team_id`, not
the display name. Known spelling variants are retained in labels but collapse
to their ids.

| season | indexed | awarded excluded | played CSV | teams by id |
|---|---:|---:|---:|---:|
| 2021/2022 | 380 | 0 | 380 | 20 |
| 2022/2023 | 342 | 29 | 313 | 19 |
| 2023/2024 | 380 | 1 | 379 | 20 |
| 2024/2025 | 342 | 1 | 341 | 19 |
| 2025/2026 | 306 | 0 | 306 | 18 |
| 2026/2027 | 99 | 0 | 99 | 18 |

The two extra awarded rows outside 2022/2023 contradict the coordinator's
summary that only the earthquake season has awarded rows; they are not
silently retained. The exclusion rule is applied by flag for all seasons.

## Coverage and levels

The complete per-season coverage matrix, including every stat key used by the
analysis, is in `analysis/eda_numbers.json`. Headline levels are:

| season | goals | SOT | corners | total shots | stats cards | referee |
|---|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 2.808 | 9.026 | 9.553 | 25.337 | 3.561 | 50.0% |
| 2022/2023 | 3.048 | 9.262 | 9.690 | 26.073 | 4.284 | 100.0% |
| 2023/2024 | 2.794 | 8.799 | 9.520 | 25.728 | 4.203 | 100.0% |
| 2024/2025 | 2.935 | 8.947 | 9.724 | 25.601 | 4.654 | 100.0% |
| 2025/2026 | 2.654 | 8.516 | 9.438 | 25.660 | 4.464 | 91.5% |
| 2026/2027 | 3.010 | 9.515 | 9.394 | 27.798 | 3.828 | 100.0% |

Coverage confirms the supplied pattern with played-row denominators: stats
100% throughout; shotmap 2.9% in 2021/2022 and 100% thereafter; period splits
0.5%, 28.4%, then 100%. xG is absent in 2021/2022 and present in every later
played row. Referee text is blank in half of 2021/2022, then complete except
2025/2026 at 91.5%. No played score-only/stub rows were found. Cards are
stats-source in 1,771 of 1,818 rows; 47 rows use the event fallback under
the broken-stats rule below.

## xGOT and cards

xGOT populated-shot shares are 40.9%, 34.6%, 33.5%, 99.5%, 99.7%, and 99.7%
by season. The field changes meaning before 2024/2025 and is era-guarded to
2024/2025 onward. Cards use the stats feed after the dev-only agreement check:
exact agreement 84.9%, stats lower 14.4%, stats higher 0.7%, mean
stats-minus-events −0.241 yellows/match (n=1,413; 2021/2022–2024/2025).
BROKEN-STATS RULE (frozen from dev-era evidence, before any fitting):
the agreement gap is concentrated in matches whose stats discipline
block is zeroed — stats yellows 0–0 while the event feed records yellows
(47 matches warehouse-wide: 43 in 2021/2022, 1 in 2023/2024, 3 in
2025/2026; other stat keys in those matches are intact and 3 even carry
stats reds > 0, so the yellow fields alone are broken). For those
matches the unified target falls back to event yellows
(`cards_source='events_broken_stats'`), exactly like the BE
stats-absent fallback. Genuine 0–0 matches (both feeds zero, n=48) are
untouched. With the rule, the dev unified mean is 4.281 yellows/match
and the dev over-rate at 4.5 is 0.436. Event counts otherwise remain
`ev_*` audit columns only.
