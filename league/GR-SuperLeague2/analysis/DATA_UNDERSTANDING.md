# Phase 1 — Data Understanding: FotMob Greece Super League 2 Warehouse

## 0. Integrity headline

The index contains 1,935 league_id 8815 rows and the builder produces
1,935 unique match rows plus 3,870 team-match rows. Season counts are
546, 420, 364, 261, 265, and 79 (2026/2027 in progress). Team counts
per season are 34, 30, 24, 20, 20, and 16 distinct FotMob team ids
(58 distinct ids across the corpus). `parentLeagueId` is always 8815.
Every row is a finished match with a parseable FT score; there are no
duplicate match ids and no cancelled matches.

This is a **scores-only league**: `content.stats` is null and the
shotmap is empty in **all 1,935 payloads** (verified payload by
payload by the builder, which asserts it and would raise on any
stats-carrying payload — the index's `has_stats` flag is not trusted,
per programme rule). There is no SOT, corners, total-shots, xG,
referee, or period-split data anywhere in the corpus. The only
per-match quantities are the FT score and the event feed (goals and
cards, present in 89.7% of matches).

## 1. Format and the phase rule

The league shrank and changed shape twice across the corpus. The feed
labels every match through `general.leagueName`; the phase is taken
from `leagueName` ONLY (the BE/GR rule):

| Season | regular | promotion group | relegation group | other | total |
|---|---:|---:|---:|---:|---:|
| 2021/2022 | 544 (2 groups × 17, double RR) | — | — | 2 (promotion playoff final, 2 legs) | 546 |
| 2022/2023 | 420 (2 groups × 15, double RR) | — | — | — | 420 |
| 2023/2024 | 264 (2 groups × 12, double RR) | 40 (2 × 5 teams, double RR) | 60 (2 × 6 teams, double RR) | — | 364 |
| 2024/2025 | 180 (2 groups × 10, double RR) | 40 (2 × 5, double RR) | 40 (2 × 5, double RR) | 1 (Super Cup) | 261 |
| 2025/2026 | 180 (2 groups × 10, double RR) | 24 (2 × 4, double RR) | 60 (2 × 6, double RR) | 1 (Super Cup) | 265 |
| 2026/2027 | 79 so far (single group, 16 teams) | — | — | — | 79 |

Format notes: two geographical groups (North/South, then Grp. A/B)
through 2025/2026, with promotion/relegation groups added from
2023/2024; **2026/2027 is a single 16-team group** — a format break,
and that season is in progress. The 2021/2022 promotion playoff was
a two-legged final (Veria vs Levadiakos, 0–1 / 1–0). The Super Cup
is a one-off final between group winners (AE Larissa 1–0 Kifisia,
2025-05-11; Kalamata 1–0 Iraklis, 2026-03-28). The builder asserts
these per-season phase counts exactly.

**Phase rule (frozen):** phase values `regular`,
`playoff_promotion`, `playoff_relegation`, `playoff`, `supercup`
are flagged in the CSV from `leagueName`; ALL phases are ordinary
rows in every fit and every window; no phase feature anywhere
(BE/GR precedent). Measured complete-season goal levels by phase:
regular 2.297 (n=1,588), promotion 2.635 (n=104), relegation 2.188
(n=160), playoff final 1.000 (n=2), Super Cup 1.000 (n=2). The
promotion-group level swings wildly by season (3.05 in 2023/2024,
2.70 in 2024/2025, 1.83 in 2025/2026) — phase means are noisy, and
no phase adjustment is attempted.

## 2. B teams (frozen rule)

Six reserve sides appear, always ineligible for promotion but playing
full seasons, including in promotion groups (AEK Athens B played the
2023/2024 promotion group; Asteras Tripolis B and Olympiacos B played
the 2025/2026 promotion groups — B teams are NOT excluded from the
promotion groups by the competition). B-team matches are 528 of
1,935 (27.3%); 22 matches are B-vs-B. The B teams, by season:
Olympiacos B, PAOK Thessaloniki FC B, AEK Athens B, Panathinaikos B
(2021/2022–2023/2024); AEK Athens B, Asteras Tripolis B, PAOK B
(2024/2025); Asteras B, Olympiacos B, PAOK B (2025/2026–2026/2027).

**B-team rule (frozen): B teams are kept as ordinary teams — every
match involving one is an ordinary row, no B-team feature, no
exclusion.** Evidence (EDA F5): B teams score 1.222 and concede
1.231 per match against a league team mean of 1.152 — gaps of only
+0.070 / +0.079, i.e. B teams are essentially league-average sides
that play slightly more open football (B-involved matches average
2.455 goals vs 2.249 without a B team; home-win rate identical,
44.9% vs 45.0%). Excluding them would delete 27% of the corpus and
break the round-robin structure for no measurable reason. Their
promotion-ineligibility affects only end-of-season incentives, and
no incentive feature is admissible anywhere in the programme.

## 3. Coverage measured from content (not index flags)

| Season | n | stats | shotmap | referee | events | HT-validated |
|---|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 546 | 0.0% | 0.0% | 0.0% | 87.9% | 87.7% |
| 2022/2023 | 420 | 0.0% | 0.0% | 0.0% | 84.5% | 83.3% |
| 2023/2024 | 364 | 0.0% | 0.0% | 0.0% | 92.0% | 92.0% |
| 2024/2025 | 261 | 0.0% | 0.0% | 0.0% | 92.7% | 92.7% |
| 2025/2026 | 265 | 0.0% | 0.0% | 0.0% | 94.3% | 94.3% |
| 2026/2027 | 79 | 0.0% | 0.0% | 0.0% | 93.7% | 93.7% |

`coverageLevel` is `lower` for all 1,935 matches. The event feed is
the only sub-FT structure in the corpus, and it is validated per
match (see §4).

## 4. Event-feed goal validation (HT provenance)

The HT goal split comes from goal-event times (`time <= 45`, the
GR-SuperLeague convention; event times are capped at 45/90, i.e.
stoppage-time first-half goals are recorded at minute 45, and no
goal event has a missing time). The feed is checked per match: the
event goals must reproduce the FT score.

- 1,736 matches carry an event feed; 1,730 validate exactly
  (99.65%). The 6 mismatches are feed errors, not close calls:
  Zakynthos–Rhodos 2022-03-06 lists 5 home-goal events against a
  0–3 score; Iraklis–Apollon Larissa 2023-03-12 lists 1 of 6 goals;
  Olympiacos B–Kifisia 2023-01-07 lists no goal events against a
  0–3 score; three more list 2 of 3 goals. Those 6 matches carry
  `ht_validated = 0` and are excluded from the halves constant.
- 199 matches have no event feed at all: 164 are 0–0 (HT is trivially
  0–0 but the builder records `ht_source = none` rather than
  inferring it), and 35 are 3–0 / 0–3 results with no events —
  awarded walkovers/forfeits (28 of them in 2022/2023). Their FT
  scores stand in the table and enter the goals fit as ordinary
  rows; only their HT split is unknown.

## 5. Definition and provenance rules

- FT score: `header.status.scoreStr`.
- HT goals: goal events at `time <= 45`, only on `ht_validated`
  matches; `ht_source` records `events` / `none`.
- Event Yellow / YellowRed / Red counts are carried as descriptive
  columns only — there is no cards target (no stats feed to unify
  against, and event cards are sparse: 337 Card events in 1,935
  matches).
- Team identity is the FotMob team id. Same-id renames in the corpus:
  Kallithea / Athens Kallithea FC (7975), Iraklis / Iraklis Saloniki
  (8675), PAOK Thessaloniki B / PAOK Thessaloniki FC B (1303118).
  `AE Iraklis Larissa` (1291837) is a different club from Iraklis
  (8675) despite the similar name.
- Season labels are the warehouse labels (`2021/2022` …
  `2026/2027`); match order is (date, match_id).

## 6. What is NOT buildable (payload-level evidence)

SOT, corners, cards, and total shots have **no target in any
payload**: zero stats rows, zero shotmap rows, zero referees, zero
period splits in 1,935 matches. The index agrees (`has_stats`,
`has_shotmap`, `has_period_splits` all False throughout), but the
decisive evidence is the payload scan, not the flags. Only the
goals candidate is buildable in this league.
