# Step 1 — Data Understanding: CO-Superliga (FotMob 11536)

## What this competition is

The Colombia Superliga is **not a league**. It is an annual two-legged
Final between the two champions of the Colombian Primera A season
(Apertura champion vs Clausura champion). Every payload's
`content.matchFacts.infoBox` confirms it: `roundName: "Final"`,
`legInfo.bestOf: 2`, `1st leg` / `2nd leg`. One tie per year, two matches
per year, nothing else.

## Inventory (warehouse index, verified against payloads)

| Season | Matches | Tie | Aggregate | Winner (decider) |
|--------|---------|-----|-----------|------------------|
| 2021 | 2 | América de Cali vs Santa Fe | 5–3 | Santa Fe (FT) |
| 2022 | 2 | Deportivo Cali vs Tolima | 2–1 | Tolima (FT) |
| 2023 | 2 | Deportivo Pereira vs Atlético Nacional | 5–3 | Atlético Nacional (FT) |
| 2024 | 2 | Junior FC vs Millonarios | 2–1 | Millonarios (FT) |
| 2025 | 2 | Atlético Nacional vs Bucaramanga | 1–1 | Atlético Nacional (Pen 3–4) |
| 2026 | 2 | Junior FC vs Santa Fe | 4–1 | Santa Fe (FT) |

**Total: 12 matches, 6 seasons, exactly 2 per season.** Index row count
(12) equals payload count (12); no missing or extra matches. All 12
finished, none cancelled/awarded. No season is in progress.

## Field coverage per season (PAYLOAD-VERIFIED, not index flags)

Scores exist in 12/12 (from `header.teams[].score`, cross-checked against
`content.matchFacts.events` goals: 29 goals in both counts).

| Field | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 | Total |
|-------|------|------|------|------|------|------|-------|
| Score | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 12/12 |
| `content.stats` (Periods All/1H/2H) | 0/2 | 0/2 | 2/2 | 1/2 | 2/2 | 2/2 | **7/12** |
| Shotmap with shots > 0 | 0/2 | 0/2 | 0/2 | 0/2 | 2/2 | 2/2 | **4/12** |
| Card events | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 12/12 |
| Referee field | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | **0/12** |
| Lineup | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 12/12 |

Index-flag vs payload discrepancies (same false-positive class as
TH2/DK-1/ID/BRC/EE/FNL/FI-YK):

- The index says `has_stats=True` for 2023 leg 1, 2023 leg 2, 2024 leg 1,
  2025 ×2, 2026 ×2 — those 7 are genuinely present. But it also says
  `has_shotmap=True` for 2025 ×2 and 2026 ×2 while `shotmap.shots` is
  empty (`[]`) in every payload before 2025; the flag tests key presence,
  not non-empty shots. Real shotmap coverage is 4 matches (2025–2026),
  114 shots total.
- 2024 leg 2 (Millonarios 2–0 Junior FC, 2024-01-25) has
  `has_stats=False` in the index and `content.stats` genuinely absent —
  the only stats gap inside the 2023+ era; its pair (2024 leg 1) has stats.
- `yellow_cards` in `content.stats` is **zero-filled in the pre-2025
  era**: [0, 0] in all three 2023/2024 stats matches despite 9, 10 and 5
  Card events in those same matches. Plausible values ([3,4], [4,5],
  [2,3], [5,4]) appear only from 2025. The stat field cannot be trusted
  before 2025; the events feed is the only card source, and it carries no
  referee.

## Format rules (frozen, from payloads)

- Two legs, home/away reversed; the second leg carries
  `header.status.aggregatedStr` and `whoLostOnAggregated`.
- No away-goals rule is evidenced: the only level aggregate (2025, 1–1)
  went **straight to penalties** (Pen 3–4, Atlético Nacional won);
  `firstExtraHalfStarted` / `secondExtraHalfStarted` are empty in all 12
  payloads, so there is no extra time. All other ties were decided on
  aggregate at full time.
- Kickoffs are in January/February (2021 is the exception: October),
  i.e. the tie opens the calendar year, before the Primera A season.

## Teams

9 distinct clubs in 6 years; each tie is a fresh pairing of that year's
two champions. Appearances (matches): Santa Fe 4, Atlético Nacional 4,
Junior FC 4, América de Cali 2, Deportivo Cali 2, Tolima 2, Deportivo
Pereira 2, Millonarios 2, Bucaramanga 2. No club plays more than 2
matches in any season; the most frequent clubs have 4 matches in 6
years. **No team has any within-competition history to learn from**:
every season's two teams arrive with zero prior Superliga matches that
season, and at most 2 stale matches (1–5 years old) from an earlier tie.

## The feasibility question (answered here, before any fitting)

A season-blocked walk-forward dev needs seasons with enough matches for
a team rating to exist and for LL / calibration to be estimated. Here a
"season" is 2 matches between 2 teams that never meet again in the
competition. The three-legged gate cannot be evaluated: the virgin
window (2026) is n=2, where the calibration SE at any line is ≈33–35pp
— 33× the 1pp clean-PASS threshold — so a PASS/FAIL would be decided by
a single goal. Pooling all 12 matches does not save it either
(OU 2.5 SE ≈ 13.6pp at n=12). See `prereg/PREREG_CO_SUPERLIGA.md` for
the arithmetic. **Verdict: not buildable — all five candidates.**
No model is fitted, no virgin is read, no engine is built.
