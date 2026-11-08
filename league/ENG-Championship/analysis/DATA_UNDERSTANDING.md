# Phase 1 — Data Understanding: FotMob England Championship Warehouse

Corpus: `data_enrichment/fotmob_world/England/Championship/` — 2,963 full
matchDetails JSONs (league_id 48), seasons 2021/2022 → 2026/2027 (the
conveyor's joint-largest corpus). Every number below was measured on
the files via the index (`fotmob_world_index.csv`, league_id = 48)
and the built CSV (`analysis/eda_compute.py` → `eda_numbers.json`).

## 0. Integrity headline

- 2,963 index rows = 2,963 files = 2,963 built match rows; match ids
  unique; every match finished. Index depth flags: stats 100%,
  shotmap 99.9% (4 matches without a shotmap) — confirmed by content.

## 1. League format — 46 rounds + promotion play-offs (the honest quirk)

24 teams, double round-robin: rounds 1–46 = **552 regular matches**
per season. Then the promotion play-offs: two-legged semi-finals
(3rd–6th) + a single final = **5 matches**, recorded by FotMob with
`matchRound` = `1/2` (semis) and `final`. There is no split/relegation
round. Play-off matches are 90-minute league-format matches between
Championship clubs, so — mirroring the SCO split decision — they are
**included as ordinary rows** with `phase='playoff'` recorded; no
phase feature is used anywhere. (Finals can reach extra time in
reality; the corpus rows carry the regulation score in `scoreStr`
as stored by FotMob — no extra-time stat periods were fabricated.)

**Warehouse gap (measured, not a bug in our builder):** the
2025/2026 copy holds only 3 of the 5 play-off matches — one
semi-final tie (Middlesbrough's) is absent, although the final
(Hull City–Middlesbrough, 2026-05-23) is present. Regular season is
complete (552). Virgin n is therefore 555, not 557.

**Churn — the defining structural fact.** Every season 6 of the 24
clubs (25%) are new: 3 relegated from the Premier League + 3 promoted
from League One replace 3 promoted + 3 relegated. 44 distinct clubs
appear across the corpus. Both adjacent tiers are in the warehouse
(Premier League id 47, n=2,000; League One id 108, n=2,943, same
seasons), so mover entry strength is directly measurable (EDA F4):
clubs arriving from the PL enter at GD **+0.490/match** (GF 1.574,
GA 1.084 vs league mu 1.265), clubs arriving from L1 at **−0.154**
(GF 1.234, GA 1.387). Parachute-payment distortion is visible in the
trait spread (career GD/match: Leeds +1.116, Burnley +0.897, Ipswich
+0.739 at the top; Rotherham −0.685 at the bottom; SD of team GD
means 0.427) — wide, but well short of SCO's Old Firm (SD 0.714).
Ratings must be allowed to be strong; no arm clamps them.

Calendar: autumn–spring (Aug–May); 2026/2027 is partial (180 matches
through 2026-11-07) and is reserved as the confirmatory window.

**Virgin-window choice (frozen here, before fitting):** the task
brief framed 2025/2026 as "in progress (transitional)". Measurement
says otherwise: the season is complete — regular season through
2026-05-02 and the play-off final on 2026-05-23 are all in the
warehouse. We therefore freeze **virgin = 2025/2026 (complete,
n=555)**, exactly paralleling SCO's use of its most recent complete
season, and reserve partial 2026/2027 as confirmatory, unread.
2024/2025 stays inside the dev window as its last evaluation season.

## 2. Coverage matrix (share of matches with real content)

| Season | n | Stats FT | Stats per half | Shotmap | xG | touches_opp_box | Referee |
|---|---|---|---|---|---|---|---|
| 2021/2022 | 557 | 100% | 3.1% | 100% | 100% | 79.2% | 48.3% |
| 2022/2023 | 557 | 100% | 19.6% | 99.8% | 100% | 78.5% | 99.8% |
| 2023/2024 | 557 | 100% | 100% | 100% | 100% | 100% | 100% |
| 2024/2025 | 557 | 100% | 100% | 100% | 100% | 100% | 100% |
| 2025/2026 | 555 | 100% | 99.5% | 99.5% | 100% | 100% | 97.3% |
| 2026/2027 (partial) | 180 | 100% | 100% | 100% | 100% | 100% | 100% |

- Full xG-era corpus from 2021/2022: stats-feed xG with open-play /
  set-play / non-penalty splits, SOT, corners, cards, big chances in
  every match.
- Per-half stats are near-absent in 2021/2022 (3.1%), partial in
  2022/2023 (19.6%), complete from 2023/2024. Halves constants are
  measured on the complete era only (2023/2024–2025/2026, EDA F3).
- `expectedGoalsOnTarget` (xGOT) population break: <1% of shots in
  2021/2022–2023/2024, 93.7–95.3% from 2024/2025 — same break as SCO.
- Referee (`matchFacts.infoBox.Referee.text`) is an empty string in
  51.7% of 2021/2022, ~100% populated thereafter.

## 3. Definition alignment (measured)

| Concept | Source | Check |
|---|---|---|
| FT score | `header.status.scoreStr` | source of truth |
| HT score | goal events `time ≤ 45` | events present in every match |
| SOT | stats feed `ShotsOnTarget` | source of record (shotmap kept as aggregates) |
| Total shots | stats feed `total_shots` | source of record |
| Cards | stats feed `yellow_cards` | stats total == event Yellow total in 91.3% of matches; season means differ by ≤0.04/match both ways (no systematic undercount of the AR/BR/NO kind) → stats feed is the unified source (`cards_source='stats'`) |
| Team xG | stats feed `expected_goals` | goals/xG per season 0.994–1.058 — calibrated, no systematic bias |
