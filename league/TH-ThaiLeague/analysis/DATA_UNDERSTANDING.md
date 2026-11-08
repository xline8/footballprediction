# Step 1 — Data Understanding: TH-ThaiLeague (FotMob id 8984)

Source: FotMob world warehouse, index `data_enrichment/fotmob_world_index.csv`
filtered `league_id = 8984`: **1,262 matches**. All numbers below are computed
by `analysis/eda_compute.py` into `eda_numbers.json` / `inventory_summary.json`
from the CSV built by `data/build_data.py`; the coordinator independently
recomputed the coverage, cards-artefact and season-mean figures from the raw
payloads and they agree.

## Inventory

| Season | Matches | Teams | Dates | Stats | Period splits | Shotmap/xG | Referee text |
|---|---|---|---|---|---|---|---|
| 2021/2022 | 240 | 16 | 2021-09-03 – 2022-05-04 | 0 | 0 | 0 | ~0 |
| 2022/2023 | 240 | 16 | 2022-08-12 – 2023-05-12 | 240 | 49 | 0 | 219 |
| 2023/2024 | 240 | 16 | 2023-08-11 – 2024-05-26 | 240 | 240 | 0 | 215 |
| 2024/2025 | 240 | 16 | 2024-08-09 – 2025-04-30 | 240 | 240 | 1 | 235 |
| 2025/2026 | 240 | 16 | 2025-08-15 – 2026-05-10 | 240 | 240 | 240 | 9 |
| 2026/2027 | 62 | 16 | 2026-09-04 – 2026-11-08 | 62 | 62 | 62 | 62 |

Totals: stats 1,022/1,262 (81.0%), shotmap 303 (24.0%), period splits 831.

## Format and calendar

Split-year seasons, roughly August–May. **16 teams every season, single
regular phase, double round-robin, 30 rounds, exactly 240 matches per
complete season.** `content.hasPlayoff` is False or absent in every payload;
there is no championship split, relegation round or play-off in this era.
Phase rule frozen: every row is `phase = regular`. The 2026/2027 season is
in progress (62 matches at warehouse freeze) and is the reserved
confirmatory window — never read in this build. The last COMPLETE season,
2025/2026, is the virgin for every candidate.

## Team identity

28 distinct FotMob team ids across the six seasons. The coordinator verified
from the raw payloads: **no team id carries more than one name and no name
maps to more than one id**; names are Latin-script throughout. No rename
handling is needed; all team logic keys on team id. Three clubs are
promoted/relegated each season in the usual pattern (see EDA movers).

## Field coverage and quirks

- **2021/2022 is score-only** (plus goal/card events and HT scores derivable
  from goal events). It can seed the goals fit and nothing else.
- **Stats era starts 2022/2023**: `total_shots`, `ShotsOnTarget`, `corners`,
  `yellow_cards`, `red_cards`, `BallPossesion`, `big_chance`, `fouls` on all
  240 matches. `touches_opp_box` is partial early (174/240 in 2022/2023,
  203/240 in 2023/2024, full from 2024/2025).
- **xG era starts inside the virgin**: `expected_goals` (and set-play /
  open-play / non-penalty / on-target splits) and shotmaps exist only in
  2025/2026, 2026/2027 and a single 2024/2025 match. Consequence: the goals
  model is goals-only (X1 dropped), and X3/X4/X6 have no dev-era data.
- **Period splits** (`stats.Periods.FirstHalf/SecondHalf`): 49 matches in
  2022/2023, complete from 2023/2024. A legitimate halves source exists for
  every market (goal events give HT goals in all eras; split stats give
  SOT/corners/total shots/yellows from the split era).
- **Referee** (`matchFacts.infoBox.Referee.text`): good coverage in the dev
  era (215–235 per season) but **collapses to 9/240 in the virgin
  2025/2026**. Any referee feature would be unusable exactly where it must
  predict; combined with its weak reliability (EDA) X8 is dropped.

## The cards artefact — present, era-flipped

The known cross-league stats-vs-events artefact was checked first, per
season (stats-feed yellow mean vs event-unified yellow mean per match;
exact agreement = both teams' counts equal):

| Season | Stats mean | Event-unified mean | Exact agreement (match) |
|---|---|---|---|
| 2022/2023 | 3.058 | 0.113 | 0.246 |
| 2023/2024 | 4.338 | 0.096 | 0.013 |
| 2024/2025 | 4.096 | 0.021 | 0.033 |
| 2025/2026 | 4.088 | 4.279 | 0.896 |
| 2026/2027 | 3.661 | 3.774 | 0.935 |

In the dev era the **event feed is the broken one**: it contains NO plain
"Yellow" card events at all in 2021/2022–2024/2025 (only Red and YellowRed
events are published; verified by direct payload inspection — e.g. match
3934963 has stats yellows 3–1 and zero card events of any kind). An
event-unified target in dev would have mean ≈0.1 yellows/match and is not a
cards target at all. In the virgin era events are complete (1,009 Yellow +
18 YellowRed) and the classic direction appears: stats undercount the
unified count (4.088 vs 4.279/match; both-sides exact agreement 89.6% of
matches, 94.6% of team-matches).

**Frozen consequence (recorded in PREPROCESSING and the cards prereg):**
the cards target is the **stats-feed `yellow_cards`** in dev AND virgin —
the only target that exists consistently across both windows. The virgin
event-unified count is carried as a preregistered sensitivity in the cards
verdict (gate arithmetic stays on the stats target). This deviates from
the programme's usual "use event-unified when the artefact is present"
rule for a stated reason: here the unified target does not exist in the
dev window, and mixing targets (stats dev / unified virgin) would break
gate comparability.
