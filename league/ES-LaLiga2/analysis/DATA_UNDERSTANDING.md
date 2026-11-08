# Phase 1 — Data Understanding: FotMob Spain LaLiga2 Warehouse

Corpus: `data_enrichment/fotmob_world/Spain/LaLiga2/` — 2,478 full
matchDetails JSONs (league_id 140), seasons 2021/2022 → 2026/2027.
Resumed from `CHECKPOINT_HOLD_2026-11-09.md` (the hold-time inventory:
n, stats, period splits, shotmap, play-off shape, LaLiga in-warehouse —
all confirmed by the full build below). Every remaining Step-1 item the
checkpoint listed is measured here: expected_goals key coverage per
season, referee coverage, the cards stats-vs-events check (dev-era
evidence), the stat-key inventory, the churn table, and the virgin
freeze. Numbers from the built CSV (`data/build_data.py`) and
`analysis/eda_compute.py` → `eda_numbers.json`, independently
recounted by the coordinator from the index (goals per season match
to the third decimal).

## 0. Integrity headline

- 2,478 index rows = 2,478 files = 2,478 built match rows; match ids
  unique; every match finished. Index depth flags: stats 100% in
  every season — confirmed by content.

## 1. League format — 42 rounds + promotion play-offs

22 teams, double round-robin: rounds 1–42 = **462 regular matches**
per season. Then the promotion play-offs (3rd–6th): two-legged
semi-finals + a two-legged final = **6 matches**, recorded by FotMob
with `matchRound` = `1/2` (semis ×4) and `final` (×2). There is no
split/relegation round. Play-off matches are 90-minute league-format
matches between LaLiga2 clubs, so — mirroring the ENGCH/SCO decision —
they are **included as ordinary rows** with `phase='playoff'`
recorded; no phase feature is used anywhere. Unlike ENGCH, the
warehouse copy is complete: every finished season holds all 468.

**Churn — the defining structural fact (by team_id).** Every season
exactly **7 of the 22 clubs (32%) are new**: 3 relegated from LaLiga
+ 4 promoted from Primera Federación replace 3 promoted + 4 relegated.
42 distinct clubs (team ids) appear across the corpus. Both adjacent
tiers are in the warehouse (LaLiga id 87, n=2,019; Primera Federación
id 8968, n=4,081, same seasons), so mover entry strength is directly
measurable (EDA F4): clubs arriving from LaLiga enter at GD
**+0.251/match** (GF 1.271, GA 1.020 vs league mu 1.191), clubs
arriving from Primera Federación at **−0.136** (GF 1.166, GA 1.302).
The step down from LaLiga is worth about half the ENGCH Premier
League step (+0.49); the step up from the third tier is mostly a
defensive problem (GA +0.111) with attack near league average.

**Team-identity quirk (measured, load-bearing).** 10 of the 42 FotMob
team ids carry **two name spellings** across seasons — accents are
dropped in some payloads (`Cadiz`/`Cádiz`, `Cordoba`/`Córdoba`,
`Castellon`/`Castellón`, `Deportivo Alaves`/`Deportivo Alavés`, …).
Raw-name set arithmetic therefore invents phantom clubs (a first pass
counted 23–27 "teams" per season and 52 overall). The truth, by
team_id: exactly 22 per season, 42 overall, 7 entries per season.
Spellings map 1:1 onto ids with no collisions, so accent-normalised
name matching is exact where only names exist (the warehouse index).
**All state in this league is keyed on team_id; names are display
only.** (First-pass name-keyed churn/mover numbers were recomputed
and replaced before any design quantity was frozen.)

Calendar: autumn–spring (Aug–Jun, play-offs into June); 2026/2027 is
partial (138 matches, rounds 1–13, through 2026-11-07) and is
reserved as the confirmatory window.

**Virgin-window choice (frozen here, before fitting):** 2025/2026 is
complete in the warehouse (462 regular + 6 play-offs, last matches
June 2026). We freeze **virgin = 2025/2026 (complete, n=468)**, with
dev = 2021/2022 seed + 2022/2023–2024/2025 evaluation (pooled
n=1,404) and partial 2026/2027 reserved un-read as confirmatory —
exactly the ENGCH frame. One era fact shapes the whole design: the
xG/shotmap era starts *inside* this virgin (§2), so no xG arm can be
honestly dev-tested; the goals candidate is goals-only by design.

## 2. Coverage matrix (share of matches with real content)

| Season | n | Stats FT | Stats per half | Shotmap | xG (stats key) | touches_opp_box | Referee |
|---|---|---|---|---|---|---|---|
| 2021/2022 | 468 | 100% | 0.2% | 0.2% | 0.2% (1) | 75.0% | 48.5% |
| 2022/2023 | 468 | 100% | 24.1% | 0.6% | 0.6% (3) | 77.4% | 99.8% |
| 2023/2024 | 468 | 100% | 100% | 0.0% | 0.0% (0) | 87.2% | 98.7% |
| 2024/2025 | 468 | 100% | 100% | 0.6% | 0.6% (3) | 100% | 99.0% |
| 2025/2026 (virgin) | 468 | 100% | 100% | 100% | 100% | 100% | 82.1% |
| 2026/2027 (partial) | 138 | 100% | 100% | 100% | 100% | 100% | 100% |

- **The xG era starts in the virgin.** `expected_goals` (and its
  open-play/set-play/non-penalty splits) exists in 7 of 1,872 dev
  matches and in every match from 2025/2026. Shotmap is the same
  story (613/2,478, effectively only 2025/2026 + 2026/2027; xGOT is
  populated for 99.6% of virgin-era shots). Any xG-consuming arm
  (blend X1, set-play X3, xG/shot X4, xGOT X6) would have no dev
  window to be tested on — all four are dropped on availability
  (FEATURES), and the goals Gate Zero is the production pattern's
  documented goals-only fallback, not a new design.
- Count markets are untouched by the era break: SOT, corners, total
  shots, fouls, big chances and possession are in the stats feed for
  **100% of matches in every season** — S/C/K/T all run on the stats
  feed (cards target excepted, §3 — its *definition*, not coverage).
- Per-half stats are near-absent in 2021/2022 (0.2%), partial in
  2022/2023 (24.1%), complete from 2023/2024. Halves constants are
  measured on the complete era only (2023/2024–2025/2026, EDA F3).
- `touches_opp_box` is partial in the early dev seasons (75.0–87.2%),
  100% from 2024/2025 — the X7 min-8 rule absorbs the gaps (ENGCH
  pattern, same magnitudes).
- Referee (`matchFacts.infoBox.Referee.text`) is an empty string in
  51.5% of 2021/2022, ~99% populated in 2022/2023–2024/2025, and
  drops to 82.1% in the virgin — coverage alone would not kill X8;
  its reliability does (EDA F8).

**Stat-key inventory (All period):** every other modelled key —
`total_shots`, `ShotsOnTarget`, `ShotsOffTarget`, `blocked_shots`,
`shots_inside_box/outside_box`, `big_chance`, `corners`,
`yellow_cards`, `red_cards`, `fouls`, `Offsides`, `keeper_saves`,
`BallPossesion` — is present in 100% of matches in every season. The
only keys below 100% anywhere are the xG family, `touches_opp_box`
(above) and `expected_goals_on_target` (mirrors the xG era).

## 3. Definition alignment (measured)

| Concept | Source | Check |
|---|---|---|
| FT score | `header.status.scoreStr` | source of truth |
| HT score | goal events `time ≤ 45` | events present in every match |
| SOT | stats feed `ShotsOnTarget` | source of record |
| Total shots | stats feed `total_shots` | source of record |
| Cards | **event feed** `type='Card', card='Yellow'` | stats feed UNDERCOUNTS — see below |
| Team xG | stats feed `expected_goals` | exists only from 2025/2026; goals/xG 0.966 in the virgin (descriptive only; no xG arm) |

**Cards check — run early, dev-era evidence only (2021/2022–
2024/2025), before any fitting.** The stats feed's `yellow_cards` is
not one consistent quantity in this league:

- Totals, stats vs event Yellow-only: 1,923 vs 2,180 (−11.8%),
  2,117 vs 2,336 (−9.4%), 2,135 vs 2,203 (−3.1%), 2,151 vs 2,207
  (−2.5%). The stats feed is low in **every** dev season.
- Exact per-match agreement is only 79.9–85.7% (pooled dev 82.5%).
- 51 matches in 2021/2022 and 36 in 2022/2023 have stats yellows of
  (0, 0) while the event feed shows real yellows — a discipline-block
  dropout, not a definitional difference: where the stats feed does
  agree, it agrees with Yellow-**only** event counts (agreement with
  Yellow+YellowRed is 0 matches), i.e. YellowRed is a red in both
  feeds' accounting.

Decision (the AR/BR/NO feed-artefact precedent, IN-ISL shape): the
unified cards target is the **event feed for every match** —
`yellow_*` = Yellow events by side, YellowRed/Red counted as reds,
`cards_source='events'` for all rows. Events are present in 100% of
matches in every season. Stats-feed yellows remain in
`yellow_cards_*` as the audit trail. (For the record, the virgin
shows the same pattern: 2,352 stats vs 2,387 events, 82.3% exact —
the decision taken on dev evidence holds there too.)
