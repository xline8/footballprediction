# Phase 1 — Data Understanding: FotMob Australia A-League Warehouse

Corpus: `data_enrichment/fotmob_world/Australia/A-League/` — 857 full
matchDetails JSONs (league_id 113), seasons 2021/2022 → 2026/2027.
Every number below was measured on the files via the index
(`fotmob_world_index.csv`, league_id = 113) and the built CSV.

## 0. Integrity headline

- 857 index rows = 857 files = 857 built match rows; match ids
  unique; every match finished. Index depth flags: stats 100%,
  shotmap 99.9% — confirmed by content (one 2025/2026 match has
  stats but no shotmap; see §2).

## 1. League format — regular season + Finals Series (the honest quirk)

Southern-hemisphere calendar: October–May. 12 teams in most seasons.

- **Regular season**: double/triple round-robin rounds numbered
  1–26 (12 teams, 156 matches) or 1–29 (2024/2025 only: 13 teams —
  Auckland FC joined the league, Western United still present —
  169 matches with byes).
- **Finals Series** (playoffs), 7 matches every season: 2
  elimination finals (round label `1/4`), 4 semi-final matches
  (`1/2`, two two-legged ties recorded as four matches), 1 Grand
  Final (`final`). Flagged `phase='finals'`, regular rounds
  `phase='regular'`.
- **Inclusion decision (documented, not hidden)**: finals are
  INCLUDED in every fit. Reasoning: they are the same 12 league
  teams playing the same competition programme in the same weeks;
  they are 7 of 163 matches per season (4.3%) — too few to model
  separately, and discarding them would shrink an already small
  corpus. The phase flag makes any exclusion an explicit, countable
  filter; no phase feature is used in any model.
- **Extra time**: 5 finals went to extra time (3 in 2023/2024, 2 in
  2025/2026). Their `All` stats cover >90 minutes and their
  scoreStr is the after-extra-time score. Kept, flagged
  `has_extra_time`, never silently repaired (the DK playoff-final
  precedent). 32 penalty-shootout shots exist in the corpus and are
  excluded from all shotmap aggregates.
- **No relegation**: the A-League has no promotion/relegation, so
  there are no movers and no tier offset is needed or estimable
  (contrast J.League F4). Team churn is expansion only: Auckland FC
  entered in 2024/2025 with zero in-league history — the thin-data
  newcomer case the goals candidate's SHRINK arm addresses.
  Western United left after 2024/2025.

## 2. Coverage matrix (share of matches with real content)

| Season | n | Stats FT | Stats per half | Shotmap | xG | touches_opp_box | Referee |
|---|---|---|---|---|---|---|---|
| 2021/2022 | 163 | 100% | 0% | 100% | 100% | 90.2% | 76.7% |
| 2022/2023 | 163 | 100% | 24.5% | 100% | 100% | 96.9% | 93.9% |
| 2023/2024 | 169 | 100% | 100% | 100% | 100% | 100% | 97.0% |
| 2024/2025 | 176 | 100% | 100% | 100% | 100% | 100% | 96.6% |
| 2025/2026 | 163 | 100% | 100% | 99.4% | 100% | 100% | 82.8% |
| 2026/2027 (partial) | 23 | 100% | 100% | 100% | 100% | 100% | 100% |

- This is a **full xG-era corpus from 2021/2022**: stats-feed xG
  with open-play/set-play/non-penalty splits, SOT, corners, cards,
  big chances in every match.
- Per-half stats ramp in during 2022/2023 and are complete from
  2023/2024 — halves constants are measured on the complete era
  only (2023/2024–2025/2026, n=571 with splits).
- `expectedGoalsOnTarget` (xGOT) population break: populated only
  for on-target shots in 2021/2022–2023/2024 (34–37% of shots),
  ~100% from 2024/2025. Any xGOT trait is era-guarded to 2024/2025
  onward — the same break DK showed.
- Referee (`matchFacts.infoBox.Referee.text`) coverage is
  INCOMPLETE and uneven (76.7% → 82.8% in the virgin season) —
  unlike DK/J1's near-full coverage. Combined with the failed
  strictness reliability check (EDA F8), the referee arm is not
  built for AU.

## 3. Definition alignment (measured)

| Concept | Source | Check |
|---|---|---|
| FT score | `header.status.scoreStr` | source of truth (after extra time for the 5 flagged finals) |
| HT score | goal events `time ≤ 45` | events present in 100% of matches; HT derivable for all 857 |
| SOT | stats feed `ShotsOnTarget` | shotmap aligned definition (on-target AND not blocked) correlates 0.989 with the stats total, exact in 89.3%; stats feed is source of record |
| Total shots | stats feed `total_shots` | shotmap count exact in 89.8% of matches; stats feed is source of record |
| Cards | stats feed `yellow_cards` | stats == event-feed Yellow counts in 89.7% of matches (event feed also lists YellowRed separately); stats feed is the unified source (`cards_source='stats'` everywhere) |
| Team xG | stats feed `expected_goals` | goals/xG pooled 1.002; per season 0.944–1.080 — calibrated, no systematic bias (2024/2025 +8%, 2025/2026 −6%, noted) |

## 4. Virgin-window note (brief vs measured reality)

The commissioning brief described 2025/2026 as "in progress
(transitional, like J1's 2026)". The warehouse itself shows
2025/2026 COMPLETE: 163 matches, 2025-10-17 → 2026-05-23, full
regular season + all 7 finals. It is therefore used as a complete
virgin window (the strongest form of the intended design), and the
genuinely in-progress season is 2026/2027 (23 matches at pull),
which is reserved un-read as the confirmatory window with a
season-end confirmatory read noted for when it completes
(~May 2027). Dev = the four earlier complete seasons.
