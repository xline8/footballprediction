# Step 1 — Data Understanding: Italy Serie B (IT-SerieB)

Source: FotMob world warehouse, league_id **86**, index rows **2,059**.
Numbers from the built CSV (`data/build_data.py`) and
`analysis/inventory.py` / `analysis/eda_compute.py` →
`inventory_summary.json`, `eda_numbers.json`. The coordinator
independently recounted goals per season from the index `score`
column — exact match to the third decimal in every season.

## Inventory

| Season | n / finished | Regular | Promotion PO | Relegation PO | Teams (ids) | Stats FT | Stats per half | Shotmap / xG | touches_opp_box | Referee | Events |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 390 | 380 | 8 | 2 | 20 | 100% | 1.0% | 0.8% / 1.0% | 74.4% | 47.4% | 100% |
| 2022/2023 | 390 | 380 | 8 | 2 | 20 | 100% | 28.7% | 1.3% / 1.3% | 76.9% | 97.2% | 100% |
| 2023/2024 | 390 | 380 | 8 | 2 | 20 | 100% | 100% | 0.3% / 0.3% | 99.2% | 79.7% | 100% |
| 2024/2025 | 389 | 380 | 8 | 1 | 20 | 100% | 99.7% | 0.8% / 0.8% | 99.7% | 74.0% | 100% |
| 2025/2026 | 390 | 380 | 8 | 2 | 20 | 100% | 100% | 100% / 100% | 100% | 75.4% | 100% |
| 2026/2027 | 110 | 110 | 0 | 0 | 20 | 100% | 100% | 100% / 100% | 100% | 90.0% | 100% |

This is the mirror image of IT-SerieC: **the stats feed exists in
100% of matches in every season**, so SOT / corners / cards / total
shots all have complete dev and virgin targets. What does *not*
exist before the virgin is the shotmap/xG family.

## Format — 38 rounds + play-offs/play-outs, identified in the feed

20 teams, double round-robin = **380 regular matches** per season
(`general.leagueName = 'Serie B'`, `matchRound` 1–38). The feed
labels the post-season explicitly by leagueName:

- `Serie B Promotion Playoff` — 8 matches/season: preliminary round
  `1/4` ×2 (single leg, 3rd–6th vs 7th/8th pattern), semi-finals
  `1/2` ×4 (two legs), final `final` ×2 (two legs).
- `Serie B Relegation Playoff` — the play-out, `final` ×2 (two
  legs). **2024/2025 holds only 1**: the Salernitana–Sampdoria
  return leg is absent from the warehouse (that tie's second leg
  was abandoned/awarded off-pitch) — a genuine 389-match season,
  not a parsing loss.

**Phase rule (frozen from these numbers): play-off and play-out
matches are included as ordinary rows** (`phase` recorded, no phase
feature). Justification, on Serie B's own data: they are 10 of 390
matches (2.6%), contested only by that season's Serie B clubs in
90-minute league format — the ES-LaLiga2 / ENG-Championship shape.
IT-SerieC's exclusion does not transfer: Serie C excluded 248
matches (4.0%) that were *inter-group* (clubs that never meet in
the regular season) plus a Super Cup; no such structure exists
here.

**Churn.** Exactly **7 of 20 clubs (35%) are new every season**:
3 relegated from Serie A + 4 promoted from Serie C replace 3
promoted + 4 relegated (verified by team_id, every entry season
2022/2023–2026/2027). Both adjacent tiers are in the warehouse
(Serie A id 55, n=2,011; Serie C id 147, n=6,184), so mover entry
strength is directly measurable (EDA F4).

**Team-identity quirk (measured, load-bearing).** 46 FotMob team
ids / 53 name spellings. Most variation is harmless same-id
renaming (`Parma Calcio 1913`/`Parma`, `FeralpiSalo`/`Union
Brescia` on id 189481, `Sudtirol`/`Südtirol`). One true id split:
**Reggiana** was carried as id 959006 (Aug–Nov 2023, 15 matches)
and as id 6500 (`AC Reggiana 1919`) thereafter; the two ids never
co-occur and their 2023/2024 sequences are complementary
(15 + 23 = 38). The builder canonicalises 959006 → 6500
(documented alias in `build_data.py`); after the fix every season
holds exactly 20 ids. **All state is keyed on team_id; names are
display only** (the one name-keyed test, mover membership, uses
accent-normalised names plus the alias `ac reggiana 1919` →
`reggiana`, verified against the Serie C index).

Calendar: autumn–spring (Aug–Jun, play-offs into June);
2026/2027 is partial (110 matches through 2026-11-08) and is
reserved as the confirmatory window.

**Virgin-window choice (frozen here, before fitting):** virgin =
**2025/2026 (complete, n=390)**; dev = 2021/2022 seed +
2022/2023–2024/2025 evaluation (pooled n=1,169); partial
2026/2027 reserved un-read as confirmatory. One era fact shapes
the design exactly as in ES-LaLiga2: **the xG/shotmap era starts
inside the virgin** (`expected_goals` in 13 of 1,559 dev matches;
shotmap in 12; both 100% from 2025/2026) — no xG arm can be
honestly dev-tested, so goals is goals-only by design and SOT has
no quality-input arm.

## Coverage notes

- FT score present in every finished payload; events in 100%.
- Per-half stats: 1.0% in 2021/2022, 28.7% in 2022/2023, ~100%
  from 2023/2024. Halves constants are measured on the complete
  seasons only (2023/2024–2025/2026, EDA F3).
- `touches_opp_box`: 74.4–76.9% in the first two seasons, ~100%
  from 2023/2024.
- Referee (`matchFacts.infoBox.Referee.text`): 47.4% in the seed
  season, 97.2% in 2022/2023, 74.0–79.7% after, 75.4% in the
  virgin. Coverage alone would not kill X8; its reliability does
  (EDA F8, r = 0.061).
- One 2024/2025 match lacks a stats-feed yellow on one side
  (stats yellows n=388 that season); the events feed is complete.

## Definition alignment (measured)

| Concept | Source | Check |
|---|---|---|
| FT score | `header.status.scoreStr` | source of truth |
| HT score | goal events `time ≤ 45` | events in 100% |
| SOT | stats feed `ShotsOnTarget` | 100% every season |
| Total shots | stats feed `total_shots` | 100% every season |
| Cards | **event feed** `type='Card', card='Yellow'` | stats feed UNDERCOUNTS — §below |
| Team xG | stats feed `expected_goals` | only from 2025/2026; goals/xG 0.986 in the virgin (descriptive) |

**Cards check — run early, dev-era evidence only
(2021/2022–2024/2025), before any fitting.** The stats feed's
`yellow_cards` undercounts the event feed in **every** dev season:
totals stats vs events 1,952 vs 2,016 (−3.17%), 1,877 vs 1,953
(−3.89%), 1,936 vs 1,975 (−1.97%), 1,878 vs 1,909 (−1.62%).
Exact per-match agreement is only 79.7–89.7%, and agreement with
Yellow+YellowRed is *lower* in every season (the stats feed tracks
Yellow-only where it agrees). 0–5 matches per season have stats
(0,0) with real event yellows. Decision (the ES/AR/IN feed-artefact
precedent): the unified cards target is the **event feed for every
match** — `yellow_*` = Yellow events by side, YellowRed/Red counted
as reds, `cards_source='events'` for all rows. Stats-feed yellows
remain in `yellow_cards_*` as the audit trail. The virgin shows
the same pattern descriptively (1,667 stats vs 1,701 events,
87.4% exact) — the dev-evidence decision holds there too.
