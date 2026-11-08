# Phase 1 — Data Understanding: FotMob India Indian Super League Warehouse

Corpus: `data_enrichment/fotmob_world/India/Indian Super League/` —
653 full matchDetails JSONs (league_id 9478), seasons 2021/2022 →
2026/2027. Every number below was measured on the files via the index
(`fotmob_world_index.csv`, league_id = 9478) and the built CSV.

## 0. Integrity headline

- 653 index rows = 653 files = 653 built match rows; match ids
  unique; every match finished. Index depth flags: stats 100%,
  shotmap 100% — confirmed by content.

## 1. League format — franchise league, league stage + play-offs

Calendar: normally September/October–March/April. Franchise league
with **no promotion or relegation**; squads churn hard between
seasons (foreign-player quota + marquee turnover) — team identity is
keyed on FotMob team id and trait stability is *measured*, not
assumed (EDA F2).

- **League stage**: 110 matches (11 teams, 2021/2022–2022/2023),
  132 (12 teams, 2023/2024, Punjab FC joined), 156 (13 teams,
  2024/2025, Mohammedan SC joined). In the feed the league stage is
  labelled round `1` in 2021/2022–2023/2024 and numbered rounds
  1–26 in 2024/2025 — a labelling change, not a format change.
- **Play-offs**: 5–7 matches per season — knock-out rounds labelled
  `1/4` (2 matches, from 2022/2023), `1/2` (4 matches, two-legged
  semi-finals), `final` (1). Flagged `phase='playoffs'`, league
  stage `phase='regular'`.
- **FREEZE (inclusion rule, fixed here and in every prereg)**:
  play-off matches are INCLUDED in every fit. Same teams, same
  competition programme, same weeks; 5–7 of 91–163 matches per
  season is too few to model separately, and discarding them would
  shrink the program's thinnest corpus further. The phase flag
  makes any exclusion an explicit, countable filter; no phase
  feature is used in any model.
- **2025/2026 (the virgin season) is a format break**: the season
  started only in February 2026 and ran as a truncated single
  round-robin — 14 teams, 91 matches (13 rounds × 7), **no
  play-offs**. Hyderabad FC did not take part; Inter Kashi and
  SC Delhi debuted with zero in-league history. It is nonetheless
  COMPLETE (finished 2026-05-21, and 2026/2027 is under way), so it
  is the honest virgin window: most recent complete season.
- **Extra time**: 3 play-off matches carry extra-time periods
  (1 each in 2022/2023, 2023/2024, 2024/2025). Their `All` stats
  cover >90 minutes. Kept, flagged `has_extra_time`, never
  silently repaired. Penalty-shootout shots are excluded from all
  shotmap aggregates.
- **2021/2022 quirk**: the season was played largely in a Goa
  bubble (neutral venues behind closed doors). The pooled home
  edge (+0.14 goals) is the weakest in the conveyor so far
  (NO +0.42, BR +0.39); no venue correction is built — the fact
  is recorded and the DC home term is fitted as usual.

## 2. Coverage matrix (share of matches with real content)

| Season | n | Stats FT | Stats per half | Shotmap | Events | Referee |
|---|---|---|---|---|---|---|
| 2021/2022 | 115 | 100% | 18.3% (21) | 100% | 100% | 6.1% (7) |
| 2022/2023 | 117 | 100% | 2.6% (3) | 100% | 100% | 12.0% (14) |
| 2023/2024 | 139 | 100% | 100% | 100% | 100% | 12.2% (17) |
| 2024/2025 | 163 | 100% | 100% | 100% | 100% | 13.5% (22) |
| 2025/2026 (virgin) | 91 | 100% | 100% | 100% | 100% | **0% (0)** |
| 2026/2027 (partial) | 28 | 100% | 100% | 100% | 100% | 100% (28) |

- Stats-feed xG with open-play/set-play/non-penalty splits, SOT,
  corners, cards, big chances, box touches exists in **every**
  match from 2021/2022 — a full xG-era corpus.
- Per-half stats are effectively absent before 2023/2024 — halves
  constants are measured on the complete-splits dev era only
  (2023/2024–2024/2025, n=302).
- `expectedGoalsOnTarget` (xGOT) population break at **2024/2025**:
  populated only for on-target shots before (31–33% of shots,
  ≈97% of on-target shots), ~98–100% of all shots from 2024/2025.
  Any xGOT trait is era-guarded to 2024/2025 onward — which leaves
  exactly one dev season of era-valid data (see FEATURES, X6).
- **Referee coverage is the program's worst**: 88 of 653 matches
  name a referee (13.5%); the most frequent referee has 11
  matches; the virgin season has none. No referee trait can be
  measured, let alone adopted (EDA F8).

## 3. Cards feed check (run EARLY, before any fitting)

Per the conveyor lesson (AR/BR/NO all found stats-feed undercounts),
stats-feed yellows were compared with event-feed yellows
(`type == 'Card'`, `card == 'Yellow'`) on **dev-era evidence only**:

| Season | Exact agreement | Stats mean | Events mean | Net diff/match |
|---|---|---|---|---|
| 2021/2022 | 107/115 = 93.0% | 3.43 | 3.47 | −0.035 |
| 2022/2023 | 108/117 = 92.3% | 3.52 | 3.57 | −0.051 |
| 2023/2024 | 115/139 = 82.7% | 4.50 | 4.61 | −0.115 |
| 2024/2025 | 116/163 = 71.2% | 4.29 | 4.34 | −0.055 |

The stats feed undercounts in **every** dev season and agreement
degrades over time. **Decision (documented here, before any virgin
read and before any fitting): the cards target is EVENT-UNIFIED
yellows** — the NO-Eliteserien precedent. `YellowRed` events (61 in
the corpus) are not counted as yellows, the sibling-builder
convention. Stats-feed yellows stay in the CSV as `yellow_cards_*`.
(The virgin season shows the same shape — agreement 90.1%, net
−0.055 — recorded for the record; it played no part in the decision,
which was taken on the dev rows above.)

## 4. Definition alignment (measured)

| Concept | Source | Check |
|---|---|---|
| FT score | `header.status.scoreStr` | source of truth (after extra time for the 3 flagged play-off matches) |
| HT score | goal events `time ≤ 45` | events present in 100% of matches |
| SOT / corners / shots | stats feed `All` | present in 100% of matches |
| Yellows (target) | event feed, unified | §3 decision |
| xG | stats feed `expected_goals` | present in 100%; runs LOW vs goals (F11) |

## 5. Windows (frozen for the whole build)

- Dev: 2021/2022–2024/2025 (n=534); 2021/2022 is the warm-up /
  training seed, scored walk-forward seasons 2022/2023–2024/2025
  (n=419).
- Virgin: **2025/2026 (n=91, complete)**, read ONCE per candidate
  and only for arms passing the dev gate.
- Confirmatory: 2026/2027 (28 played at pull), reserved, NOT read.
- The binding constraint is the virgin's size: at n=91 a
  calibration SE is ~5pp, so the PROVISIONAL band will do real
  work. No gate is loosened because of it.
