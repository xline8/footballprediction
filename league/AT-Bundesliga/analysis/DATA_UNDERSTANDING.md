# Phase 1 — Data Understanding: FotMob Austria Bundesliga Warehouse

Corpus: `data_enrichment/fotmob_world/Austria/Bundesliga/` — 1,047 full
matchDetails JSONs (FotMob league_id 38), seasons 2021/2022 → 2026/2027,
filtered from `data_enrichment/fotmob_world_index.csv`. Every number below
was measured on the files / the Phase-2 CSV, not taken from index flags
(the index's `has_period_splits` flag understates early content in the
same way the J.League pull-time flags did; coverage here is by content).

## 0. Integrity headline

- 1,047 index rows = 1,047 files = 1,047 CSV rows; match ids unique;
  goal events reproduce `scoreStr` in **1,047/1,047** matches (zero
  mismatches — cleaner than the J.League corpus, which had 2).

## 1. Format — the Austrian split (read this before any window logic)

The Bundesliga has **12 teams**. A season (195 matches) is:

| Phase | Rounds | Matches/season | What it is |
|---|---|---|---|
| Regular | 1–22 | 132 | double round-robin, all 12 teams |
| Split | 23–32 | 60 | top-6 championship group + bottom-6 relegation group, each a double round-robin; points from the regular season are **halved** (rounded down) at the split — a standings rule, irrelevant to match-level modelling |
| Playoff | '1/2', 'final' | 3 | European play-off: semi-final(s) + final between split-group finishers for the last European slot |

Corpus totals: regular 732, split 300, playoff 15 (5 complete seasons).
Handling, honestly: **split and playoff matches are real league matches**
— same teams, same 90-minute settlement, full stats — so they stay in
every training and evaluation window. What the split changes is the
*opponent mix* (a championship-group team faces only top-6 opponents
for 10 rounds), which is a real fixture property the ratings see
through results, not a data defect. The `phase` column is carried in
both CSVs so any analysis can stratify; no phase is filtered anywhere
in this build. Format was constant across all six seasons in the
corpus (12 teams every season; no format change to model).

## 2. Coverage matrix (share of matches with real content, %)

| Season | n | FT stats | xG (+ splits) | Shotmap | Period splits | Box touches | Referee named | Lineups |
|---|---|---|---|---|---|---|---|---|
| 2021/2022 | 195 | 100 | 100 | 100 | 1.0 | 63.6 | 44.1 | 100 |
| 2022/2023 | 195 | 100 | 100 | 100 | 34.4 | ~58 | 87.2 | 100 |
| 2023/2024 | 195 | 100 | 100 | 100 | 100 | 80.5 | 82.6 | 100 |
| 2024/2025 | 195 | 100 | 100 | 100 | 100 | 100 | 94.4 | 100 |
| 2025/2026 | 195 | 100 | 100 | 100 | 100 | 100 | 91.8 | 100 |
| 2026/2027 (partial) | 72 | 100 | 100 | 100 | 100 | 100 | 100 | 100 |

Reading: this is the richest conveyor corpus so far — unlike J1 there
is **no thin era**: FT team stats (shots, SOT, corners, yellows, reds,
fouls, possession, big chances, xG with open-play/set-play/non-penalty
splits) and the shotmap exist for every match of every season. The
ramps are in the *secondary* feeds only: period splits arrive during
2022/2023 and are complete from 2023/2024; `touches_opp_box` is
sporadic before 2024/2025; referee names are missing for 56% of
2021/2022 but ≥82% from 2022/2023 (91.8% in the virgin season — the
K-J1 failure mode, a virgin window with no referees, does not occur
here).

Per-shot fields: x/y, situation, shotType, period, isOnTarget,
isBlocked ≈ 100% throughout. **`expectedGoalsOnTarget` changes
population rule by era**, exactly as in J1: populated for ~34% of
shots (on-target shots) before 2024/2025, for ~99.7% from 2024/2025.
Cross-era xGOT comparisons must respect that break (EDA F7).

## 3. Quirk register

1. **The split (above)** — the league's defining quirk; handled by the
   `phase` column, never by exclusion.
2. **2026/2027 is a partial season** (72 matches, rounds 1–12, through
   2026-11-08). It is reserved as the confirmatory window and is not
   read by any gate in this build. Its early levels run hot (3.29
   goals, 28.3 shots) — a 12-round segment, not comparable to full
   seasons.
3. **Red cards are frequent** (0.235/match — more than double J1's
   0.11). They remain excluded as a target (production cards design);
   yellows are the cards target.
4. **Referee identity** sits in `content.matchFacts.infoBox.Referee.text`
   and is sometimes an empty string (recorded as missing, never
   imputed). Coverage by season is in §2.
5. **Team identity is stable by FotMob team id** (15 ids appear across
   the corpus — 12 per season with promotion/relegation churn against
   the 2. Liga, which is outside this build's scope). Names are display
   only.
6. Stat-value typing and duplicate-key behaviour are inherited from
   the shared extractor (`league/jleague_lib.py`): duplicated keys
   across stat groups are flattened; the J.League measurement (0
   conflicts in 6,228 files) is the standing evidence for this feed
   family.

## 4. Definition alignment

| Concept | Source | Alignment |
|---|---|---|
| FT score | `header.status.scoreStr` | source of truth; events reproduce it 1,047/1,047 |
| HT score | derived from goal events (`time ≤ 45`, credited side) | same derivation validated 1,711/1,711 on J1; events exist for all 1,047 here |
| SOT | stats feed `ShotsOnTarget` | stats feed is source of record (blocked shots excluded — same definitional split as J1/top-5) |
| Total shots | stats feed `total_shots` | source of record; shotmap count kept as aggregates |
| Team xG | stats feed `expected_goals` | calibrated: goals/xG 0.92–1.00 per complete season, pooled 0.975 (EDA F11 analogue) |
| Corners / yellows / reds / fouls | stats feed, FT + per-half where splits exist | complete 100% FT |
| xGOT | per-shot `expectedGoalsOnTarget` | era break at 2024/2025 (see §2) |
