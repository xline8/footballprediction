# Phase 1 — Data Understanding: Argentina Primera B Nacional

Corpus: FotMob world warehouse, index filtered to league_id `8965`.
The builder measures the payloads, rather than trusting index presence flags.

## 0. Integrity headline

The index contains 3,966 unique finished matches with scores, dated
2021-03-12 through 2026-11-02. The analysis corpus is 3,874 group-phase
matches; 92 playoff matches are excluded by `infoBox.Tournament.leagueName`
containing `Playoff` (with competition-name/round fallbacks). Per-season
group/playoff counts are 578/12, 666/14, 648/21, 722/23, 612/22, and
648/0 for 2021–2026. The 2026 row is a virgin-window definition only: a
single table, 36 teams, rounds 1–36, 648 group matches; no 2026 descriptive
statistic is computed in Phase A.

All group match ids are unique; team rows are exactly two per match. Header
goals reconcile exactly to non-shootout goal events on all 3,874 group rows.
The one corpus mismatch is the excluded 2025 playoff Gimnasia Jujuy–Deportivo
Madryn match 5009768 (header 3, one goal event).

## 1. Payload anatomy and coverage

Relevant data are in `header.teams`, `header.status`,
`content.matchFacts.events`, and `content.matchFacts.infoBox.Referee.text`.
The event feed is absent in 75 matches in 2021 and 76 in 2022, and complete
from 2023. Group-phase event coverage is therefore 505/578 in 2021,
592/666 in 2022, and complete in the EDA seasons from 2023 onward.

`content.stats` is non-empty in 0/3,966 payloads. The 121 payloads whose
stats key exists contain only `Periods.All=None` and are false positives.
`content.shotmap.shots` is empty in all 3,966 payloads. There are no stats
period splits anywhere; event times are the only half source. Lineups are
present in 3,765/3,966 but are not used.

Referees are read only from the info-box text. Across the full indexed corpus
the verified coverage is 0/590 (2021), 604/680 (2022), 634/669 (2023),
703/745 (2024), 615/634 (2025), and 646/648 (2026). The EDA uses only
2021–2025; 2026 is not summarized.

## 2. Format eras and feed breaks

- 2021: Zona A, 17 teams, 8 matches per round over 34 rounds; Zona B, 18
  teams, 9 per round over 34 rounds.
- 2022: one table, 37 teams, 37 rounds × 18 matches.
- 2023: asymmetric zones: Zona A, 19 teams, 38 rounds × 9; Zona B, 18
  teams, 34 rounds × 9. This is not smoothed into a single format.
- 2024: one table, 38 teams, 38 rounds × 19.
- 2025: Zona A and Zona B, 18 teams each, 34 rounds × 9 each.
- 2026: virgin definition only, one table, 36 teams, rounds 1–36, 648
  group matches.

The 2021–2022 card feed has no `card='Yellow'` events: its card events are
only Red and YellowRed (145 and 187 card events in total respectively).
Thus yellow targets are deliberately unavailable, NaN rather than zero,
until 2023. From 2023 the complete event feed contains Yellow events (3,320,
3,514, and 2,965 in 2023–2025); red categories remain separate.

Team identity is FotMob `id`. The canonical display spelling is the spelling
in the most recent match for that id; the 12 accent-only spelling differences
therefore do not create duplicate teams. Team counts by season are 35, 37,
37, 38, 36, and 36. The builder asserts stats/shotmap emptiness and the
group goal-event reconciliation.
