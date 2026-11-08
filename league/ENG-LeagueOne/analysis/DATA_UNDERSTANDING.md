# Phase 1 — Data Understanding: FotMob England League One Warehouse

Corpus: `data_enrichment/fotmob_world/England/League One/` — 2,943 full
matchDetails JSONs (league_id 108), seasons 2021/2022 → 2026/2027.
Every number below was measured on the files via the index
(`fotmob_world_index.csv`, league_id = 108) and the built CSV
(`analysis/eda_compute.py` → `eda_numbers.json`).

## 0. Integrity headline

- 2,943 index rows = 2,943 files = 2,943 built match rows; match ids
  unique; every match finished. Index depth flags: stats ~100%,
  shotmap ~82% pooled — but the pooled shotmap figure hides a hard
  era break (see §2): 2021/2022 has a shotmap in only 3.2% of
  matches, every later season ~100%.

## 1. League format — 46 rounds + promotion play-offs (all present)

24 teams, double round-robin: rounds 1–46 = **552 regular matches**
per season. Then the promotion play-offs: two-legged semi-finals
(3rd–6th) + a single final = **5 matches**, recorded by FotMob with
`general.leagueName = 'League One Playoff'` and `matchRound` =
`1/2` (semis) / `final`. There is no split/relegation round and no
other competition pollutes the rows: the remaining rows carry
leagueName `League One` (2,873) or `English Football League -
League One` (45, an early naming variant of the same competition —
same rounds, same clubs). Play-off matches are 90-minute
league-format matches between League One clubs, so — mirroring the
ENG-Championship decision — they are **included as ordinary rows**
with `phase='playoff'` recorded; no phase feature is used anywhere.

**Difference from the Championship precedent (measured):** the
Championship's 2025/2026 warehouse copy was missing a semi-final
tie; League One's play-offs are **complete in every season**
(5/5 per season, finals included, e.g. the 2025/2026 final
Bolton Wanderers–Stockport County, 2026-05-24). Virgin n is
therefore the full **557** = 552 regular + 5 play-off.

**Churn — the defining structural fact.** Every season 7 of the 24
clubs (29%) are new: 3 relegated from the Championship + 4 promoted
from League Two replace 3 promoted + 4 relegated. 49 distinct clubs
appear across the corpus (≥10 matches for trait work). The tier
above is in the warehouse (Championship id 48, n=2,963, same
seasons); **League Two is NOT in the warehouse** (England has only
ids 47/48/108), so promoted clubs are identified as the new clubs
that were not in the Championship the previous season — an exact
identification in this closed promotion system, recorded as an
inference, not a warehouse read. Mover entry strength is directly
measurable on the L1 side (EDA F4): clubs arriving from the
Championship enter at GD **+0.393/match** (GF 1.544, GA 1.151 vs
league mu 1.304), clubs arriving from League Two at **−0.246**
(GF 1.177, GA 1.423). Team GD spread SD 0.427; career top
Ipswich Town +0.946, bottom Doncaster Rovers −0.686 — no rating
clamping.

Calendar: autumn–spring (Aug–May); 2026/2027 is partial (158 matches
through 2026-11-04) and is reserved as the confirmatory window.

**Virgin-window choice (frozen here, before fitting):** 2025/2026
is complete — regular season plus the play-off final on
2026-05-24 are all in the warehouse. We freeze **virgin =
2025/2026 (complete, n=557)**, exactly paralleling ENG-Championship,
and reserve partial 2026/2027 as confirmatory, unread. 2024/2025
stays inside the dev window as its last evaluation season.

## 2. Coverage matrix (share of matches with real content)

| Season | n | Stats FT | Stats per half | Shotmap | xG (stats) | touches_opp_box | Referee |
|---|---|---|---|---|---|---|---|
| 2021/2022 | 557 | 100% | 0.4% | 3.2% | 3.2% | 79.2% | 49.6% |
| 2022/2023 | 557 | 100% | 21.2% | 100% | 100% | 75.9% | 100% |
| 2023/2024 | 557 | 100% | 99.5% | 99.5% | 100% | 85.6% | 100% |
| 2024/2025 | 557 | 100% | 100% | 100% | 100% | 100% | 98.0% |
| 2025/2026 | 557 | 100% | 100% | 100% | 100% | 100% | 95.9% |
| 2026/2027 (partial) | 158 | 100% | 100% | 100% | 100% | 100% | 100% |

- **The xG era starts 2022/2023, not 2021/2022** (the TR-SuperLig
  shape, not the Championship shape): the seed season carries stats
  xG only in the 18 matches that happen to have a shotmap. Every
  xG-consuming feature (X1 blend, X3 set-play, X4 xG/shot, X6 xGOT)
  must be judged against that era: the blend falls back to
  goals-only in the seed season (definitional, as in TR), and any
  trailing xG feature is necessarily inactive early in 2022/2023.
- Per-half stats are near-absent in 2021/2022 (0.4%), partial in
  2022/2023 (21.2%), complete from 2023/2024. Halves constants are
  measured on the complete era only (EDA F3).
- `expectedGoalsOnTarget` (xGOT) population break: 0.0–0.4% of
  shots in 2021/2022–2023/2024, 94.4–96.6% from 2024/2025.
- Referee (`matchFacts.infoBox.Referee.text`) is an empty string in
  50.4% of 2021/2022, ~100% populated thereafter (95.9% in the
  virgin season).

## 3. Definition alignment (measured)

| Concept | Source | Check |
|---|---|---|
| FT score | `header.status.scoreStr` | source of truth |
| HT score | goal events `time ≤ 45` | events present in every match |
| SOT | stats feed `ShotsOnTarget` | source of record (shotmap kept as aggregates) |
| Total shots | stats feed `total_shots` | source of record |
| Cards | stats feed `yellow_cards` | stats total == event Yellow total in 89.0% of matches; season means differ by ≤0.09/match with no consistent direction (2021/2022 −0.09, others ≤0.05 both ways — no systematic undercount of the AR/BR kind) → stats feed is the unified source (`cards_source='stats'`) |
| Team xG | stats feed `expected_goals` | goals/xG per season 1.155 / 1.081 / 1.075 / 1.011 over 2022/2023–2025/2026 — goals run above xG early and converge to parity; no era inside the xG era is unusable, but the blend's early-dev seasons carry this tilt (the gate judges it) |
