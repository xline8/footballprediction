# Phase 1 — Data Understanding: FotMob Saudi Pro League Warehouse

Corpus: `data_enrichment/fotmob_world/Saudi Arabia/Saudi Pro League/`
— 1,502 full matchDetails JSONs (league_id 536), seasons 2021/2022 →
2026/2027. Every number below was measured on the files via the index
(`fotmob_world_index.csv`, league_id = 536) and the built CSV
(`analysis/eda_compute.py` → `eda_numbers.json`).

## 0. Integrity headline

- 1,502 index rows = 1,502 files = 1,502 built match rows; match ids
  unique; every match finished (the builder's finished filter drops
  none). Index flags said stats 100% / shotmap 70.6% — the shotmap
  shortfall is entirely an era effect (§2), not scattered missingness.
- One club (FotMob id 101919) appears under two spellings
  ("Al Qadsiah" / "Al Qadasiya"); the builder canonicalises team
  names by team id, so the corpus has exactly 16 teams in
  2021/2022–2022/2023 and 18 from 2023/2024 (ids, not spellings).

## 1. League format and the 2023 regime break

- 16 teams through 2022/2023 (240 matches/season, double
  round-robin), **18 teams from 2023/2024** (306 matches/season).
  No split, no playoffs, no relegation rounds: a plain round-robin
  in every season. Relegation/promotion churn exists (19 distinct
  clubs pre-break, 23 post-break, 16 present in both eras) but the
  feeder tier is not part of this league's corpus.
- **The break**: the summer-2023 foreign-star influx (the
  post-Ronaldo wave) lands exactly at the 2023/2024 boundary, and
  the data confirms it is a genuine regime break, not a narrative:
  - League scoring level: **2.677 goals/match pre → 2.959 post**
    (+0.28); OU2.5 over-rate 51.5% → 56.5%.
  - SOT 8.285 → 9.038; total shots 23.562 → 24.645; corners
    9.360 → 9.678; event yellows 4.004 → 4.074.
  - Inequality widened: SD of team goal-difference means
    **0.663 pre → 0.896 post**; Al Hilal's post-era GD/match is
    +1.863, Al Nassr FC +1.598 (pre-break best: Al Ittihad +1.333).
  - Home advantage *shrank*: home goal edge +0.269 → +0.175,
    home-win rate 45.8% → 43.0%.
  - BUT team identity largely survived: cross-era correlation of
    per-team means (16 ever-present clubs) — shots-for **0.922**,
    SOT-for 0.871, goals-for 0.779, corners-for 0.739,
    goals-against 0.608. The break is mainly a level shift plus a
    widened spread, not a reshuffle. Design consequence
    (MODEL_DESIGN): dev folds are scored on post-break seasons
    only; pre-break data may enter fits only as decayed history,
    never as scored evidence about the current league.
- Calendar: autumn–spring (Aug–May). **2025/2026 is complete**
  (306 matches, 2025-08-28 → 2026-05-21) — the commissioning
  brief's "in progress" premise was checked against the warehouse
  and does not hold; 2026/2027 is the partial season (104 matches
  through 2026-10-31) and is reserved as the confirmatory window.

## 2. Coverage matrix (share of matches with real content)

| Season | n | Stats FT | Stats per half | Shotmap | xG (stats) | touches_opp_box | Referee |
|---|---|---|---|---|---|---|---|
| 2021/2022 | 240 | 100% | 0% | 2.5% | 2.5% | 62.9% | 42.9% |
| 2022/2023 | 240 | 100% | 35.8% | 13.3% | 13.3% | 80.8% | 78.8% |
| 2023/2024 | 306 | 100% | 100% | 100% | 100% | 100% | 73.5% |
| 2024/2025 | 306 | 100% | 100% | 100% | ~100% | 100% | 70.9% |
| 2025/2026 (virgin) | 306 | 100% | 100% | 100% | 100% | 100% | **0.7%** |
| 2026/2027 (partial) | 104 | 100% | 100% | 100% | 100% | 100% | 93.3% |

- **The shotmap/xG era starts exactly at the regime break**:
  2023/2024 is the first season with a shotmap or a stats-feed xG
  in every match. Pre-break xG exists only in 6/240 and 32/240
  matches — xG-based quantities are *not estimable* pre-break
  (the nominal pre-break goals/xG ratios, 44.95 and 8.30, are
  artefacts of those handfuls of matches and are not evidence).
  Every xG feature therefore carries the era guard: usable from
  2023/2024 only; the goals blend falls back to goals-only before
  that, exactly as the reference architecture prescribes.
- Per-half stats follow the same boundary (0% / 35.8% / 100%).
  Halves constants are measured on the complete-splits era
  2023/2024–2025/2026 only (EDA F3).
- `expectedGoalsOnTarget` (xGOT) population break is later: ~36–41%
  of shots carry it in 2021/2022–2023/2024, **99.4%+ from
  2024/2025**. Any xGOT trait is era-guarded to 2024/2025 onward.
- Referee names (`matchFacts.infoBox.Referee.text`) are unusable
  as a modelling input twice over: 71–79% coverage in the post-era
  dev seasons and **0.7% in the virgin season** — a live pipeline
  could not name the referee for 2025/2026 fixtures at all.

## 3. Definition alignment (measured)

| Concept | Source | Check |
|---|---|---|
| FT score | `header.status.scoreStr` | source of truth |
| HT score | goal events `time ≤ 45` | events present in every match |
| SOT | stats feed `ShotsOnTarget` | source of record, 100% all seasons |
| Total shots | stats feed `total_shots` | source of record, 100% |
| Corners | stats feed `corners` | source of record, 100% |
| Cards | **event feed (Yellow + YellowRed)** | see §3.1 |
| Team xG | stats feed `expected_goals` | post-break goals/xG 1.074 / 1.034 / 1.032 per season — goals run 3–7% above xG post-break (quality finishing), no wild miscalibration |

### 3.1 Cards feed check — run EARLY, decided on dev-era evidence only

Measured before any fitting, on the dev era only (seasons
≤ 2024/2025; the virgin season was not consulted):

| Season | Exact agreement | Stats-low matches | Stats-high | Mean (stats − events) |
|---|---|---|---|---|
| 2021/2022 | 71.2% | 58 | 11 | **−0.850** |
| 2022/2023 | 87.1% | 25 | 6 | −0.237 |
| 2023/2024 | 89.5% | 28 | 4 | −0.147 |
| 2024/2025 | 91.5% | 23 | 3 | −0.134 |

The stats feed undercounts the event feed in **every** dev-era
season, one-directionally (stats-low outnumbers stats-high roughly
5:1 or worse). Following the AR/BR/NO conveyor precedent for exactly
this artefact, the unified yellow target is the **event feed**
(Yellow + YellowRed = every yellow card shown; events present in
100% of matches) for all seasons. The stats-feed counts stay in the
CSV as cross-check columns (`yellow_cards_*`). The undercount is
worst pre-break (−0.85/match) and narrows post-break but never
reverses — one consistent target definition is used throughout
rather than a mid-corpus switch.

## 4. Climate / venue note

Stadium city and latitude are stored per match. The two highland
venues (Abha, Khamis Mushait — ~2,000 m+) host 68 post-era matches;
their home goal edge is **−0.088** vs +0.193 for lowland venues —
the highland clubs are simply weak teams in this era, and there is
no measurable altitude advantage to model. Any climate feature
would need the standard reliability discipline; this check fails
it at the descriptive level already (EDA F10), so none is built.
