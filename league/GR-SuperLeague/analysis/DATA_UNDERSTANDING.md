# Phase 1 — Data Understanding: FotMob Greece Super League 1 Warehouse

## 0. Integrity headline

The index contains 1,261 league_id 135 rows and the builder produces
1,261 unique match rows plus 2,522 team-match rows. Season counts are
240, 240, 240, 236, 236, and 69 (2026/2027 in progress). Every complete
season has 14 teams (21 distinct team ids across the corpus).
`parentLeagueId` is always 135.

Coordinator verification note: the first Codex draft of this document
(and of EDA/FEATURES/MODEL_DESIGN/config) was a copy of the
PL-Ekstraklasa documents carrying Polish numbers; it was discarded.
The builder, `eda_compute.py` and the JSONs were genuinely Greek and
were verified by an independent recomputation from the raw warehouse
JSONs (coverage, levels and the cards check reproduced exactly). All
documents were then rewritten from the verified JSONs.

## 1. Format and the phase rule

The Greek Super League 1 plays a 14-team regular season (double
round-robin, 26 rounds, 182 matches), then splits into play-off
groups. The feed labels every match through `general.leagueName`;
`matchRound` numbering restarts inside the groups in the new format,
so the phase is taken from `leagueName` ONLY (the BE rule):

| Season | regular | championship | conference | relegation | total |
|---|---:|---:|---:|---:|---:|
| 2021/2022 | 182 | 30 (6 teams, double RR) | — | 28 (8 teams, single RR) | 240 |
| 2022/2023 | 182 | 30 | — | 28 | 240 |
| 2023/2024 | 182 | 30 | — | 28 | 240 |
| 2024/2025 | 182 | 12 (4 teams, double RR) | 12 (places 5–8) | 30 (6 teams, double RR) | 236 |
| 2025/2026 | 182 | 12 | 12 | 30 | 236 |
| 2026/2027 | 69 so far | — | — | — | 69 |

The format changed in 2024/2025 (championship group shrank from 6 to
4 teams; a Conference League group for places 5–8 was added; the
relegation group went from 8 teams single RR to 6 teams double RR).
The builder asserts these per-season phase counts exactly.

**Phase rule (frozen):** phase values `regular`,
`playoff_championship`, `playoff_conference`, `playoff_relegation`
are flagged in the CSV from `leagueName`; ALL phases are ordinary
rows in every fit and every window; no phase feature anywhere
(BE precedent). Measured complete-season goal levels by phase:
regular 2.524 (n=910), championship 2.702 (n=114), conference 2.958
(n=24), relegation 2.465 (n=144) — modest against season-to-season
swings (2.35–2.97).

Greek Super League 2 (league_id 8815, 1,935 rows) IS present in the
warehouse — contrary to the programme's initial assumption — but it
contains B teams (e.g. Olympiacos B, PAOK B) that cannot be promoted,
and this build creates no SL2 corpus. Newcomers are identified
in-corpus (present in season S, absent in S−1): only 1–2 per
transition (9 total, Greece relegates two), measured under X2 in
FEATURES, not consumed; SHRINK is the goals thin-data arm.

## 2. Coverage measured from content

| Season | n | stats All | period splits | referee | box touches | stats xG | shotmap |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 240 | 100.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 2022/2023 | 240 | 100.0% | 21.2% | 89.6% | 82.5% | 0.0% | 0.0% |
| 2023/2024 | 240 | 100.0% | 100.0% | 99.6% | 89.6% | 5.0% | 5.0% |
| 2024/2025 | 236 | 100.0% | 97.9% | 73.7% | 97.9% | 2.5% | 2.5% |
| 2025/2026 | 236 | 100.0% | 100.0% | 82.6% | 100.0% | 100.0% | 100.0% |
| 2026/2027 | 69 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |

Headline "stats ~100%" is true for the basic block (score, SOT,
corners, total shots) in every season, but the rich block (xG,
shotmap, box touches, period splits) is era-bound: period splits are
complete only from 2023/2024, and stats xG / shotmap are full ONLY
from 2025/2026 — i.e. the xG era starts inside the virgin season
(the ES lesson applies to X3/X4/X6 below). The halves constants
therefore use 2023/2024–2025/2026 (n=707 matches with splits).

Two feed artefacts, recorded plainly:

- **2021/2022 total shots are a different measurement.** That
  season's `total_shots` mean is 16.89 against 21.96–24.16 in every
  later season, and its implied on-target rate is 0.510 against
  0.315–0.362 later — not credible football; the early feed's shot
  counting differs. Goals, SOT, corners and (events) yellows in
  2021/2022 are coherent with later seasons. Consequence: the
  total-shots primary line is selected on the scored dev seasons
  (2022/2023–2024/2025), and 2021/2022 shots enter T-GR only as
  warm-up state, never as a scored target.
- **2021/2022 yellows are events-only.** The stats feed carries a
  `yellow_cards` key in only 1 of the 240 matches that season; the
  unified target falls back to event-feed yellows (the PL shape).

## 3. Definition and provenance rules

- FT score: `header.status.scoreStr`.
- HT goals: goal events at `time <= 45`.
- SOT, shots, corners, cards, xG, set-play xG, box touches,
  possession, big chances: `content.stats.Periods.All`.
- Shotmap xG and xGOT: regulation shots only; shootout attempts
  excluded.
- Referee: `content.matchFacts.infoBox.Referee.text`.
- Unified yellows: stats-feed `yellow_cards` when present,
  event-feed Yellow fallback when the stats card is absent.

The builder nulls score-only payloads rather than converting missing
stats to zero (in this corpus stats All is present for every match,
so the rule is a guard, not an active filter).

## 4. Cards check (run early, per protocol)

Among 1,017 matches carrying both a stats card and an event feed,
stats and events agree exactly on total yellows in 81.4%; stats are
lower in 15.7%, higher in 2.9%, and the mean difference is −0.250
yellows per match (max abs diff 8.0). Including YellowRed events
changes exact agreement to 80.9%. This is the same stats-vs-events
artefact seen across the programme (8th league). The unified target
stands: stats-feed yellows, events fallback only where the stats
card is absent; sources are never mixed within a match.
