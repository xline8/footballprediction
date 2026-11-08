# Step 1 — Data Understanding: ZA-PSL (FotMob id 537)

Source: FotMob world warehouse, index `data_enrichment/fotmob_world_index.csv`
filtered `league_id = 537`: **1,255 matches**. All numbers below are computed
by `analysis/eda_compute.py` into `eda_numbers.json` / `inventory_summary.json`
from the CSV built by `data/build_data.py`; the coordinator independently
recomputed the coverage, play-off, cards-artefact and season-mean figures
from the raw payloads and they agree.

## Inventory (regular season only — see the play-off rule below)

| Season | Matches | Team ids | Dates | Stats | Period splits | Shotmap/xG | Referee text |
|---|---|---|---|---|---|---|---|
| 2021/2022 | 240 | 16 | 2021-08-20 – 2022-05-25 | 0 | 0 | 0 | 0 |
| 2022/2023 | 240 | 16 | 2022-08-05 – 2023-05-27 | 239 | 60 | 0 | 82 |
| 2023/2024 | 240 | 16 | 2023-08-04 – 2024-05-25 | 238 | 237 | 0 | 69 |
| 2024/2025 | 210 | 15 | 2024-09-14 – 2025-05-24 | 210 | 210 | 0 | 62 |
| 2025/2026 | 240 | 16 | 2025-08-09 – 2026-05-23 | 240 | 240 | 240 | 13 |
| 2026/2027 | 73 | 16 | 2026-08-01 – 2026-10-31 | 73 | 73 | 73 | 53 |

Totals (regular): 1,243 matches; stats 1,000/1,243 (80.5%), shotmap 313
(25.2%), period splits 820.

## Format and calendar

Split-year seasons, roughly August–May. **Straight double round-robin, no
championship split and no relegation round in the league proper.** Two
format facts had to be verified rather than assumed:

- **Promotion/relegation play-offs ARE in the index.** 12 rows (6 in
  2021/2022, 6 in 2022/2023) carry `general.leagueName = "Premier Soccer
  League Qualification Group"` — a 3-team mini-league (the 15th-placed PSL
  club plus two second-tier clubs). These are NOT regular-season matches:
  they are excluded from the league CSV (Step 2) and from every fit.
  No play-off rows appear from 2023/2024 onward.
- **2024/2025 has 210 matches and 15 teams — that is the complete official
  season, not a warehouse gap.** Royal AM were expelled mid-season and
  their fixtures were expunged; the remaining 15 clubs played a complete
  28-round double round-robin (15 × 28 / 2 = 210). Every club has exactly
  28 matches. Royal AM does not appear in the 2024/2025 index at all.

Phase rule frozen: every kept row is `phase = regular`; the 12
Qualification Group rows are excluded outright (not modelled as a phase).
16 teams in every complete season except 2024/2025 (15, above); 30 rounds
(28 in 2024/2025). The 2026/2027 season is in progress (73 matches at
warehouse freeze) and is the reserved confirmatory window — never read in
this build. The last COMPLETE season, 2025/2026, is the virgin.

## Team identity — names are NOT stable; ids are

26 distinct FotMob team ids across the six seasons; no name maps to more
than one id, but **three ids carry two names**, because FotMob applies
club renames retroactively to part of the archive:

| Team id | Names in the corpus | What happened |
|---|---|---|
| 102099 | SuperSport United / Siwelele | Club sold and renamed Siwelele for 2025/2026; 4 matches in 2022/2023 and 13 in 2023/2024 already carry the new name |
| 149599 | Maritzburg United / Durban City | Club renamed Durban City (in the second tier 2023–2025, promoted back for 2025/2026); both names appear inside 2022/2023 |
| 102100 | AmaZulu FC / AmaZulu | Short-form name on 2 matches in 2026/2027 |

Consequence (frozen in Step 2): **all team logic keys on the FotMob team
id, never on the name**; the published name is kept per row for display
only. Keyed on id, every season has the correct 16 (15) clubs and every
club the correct match count.

## Field coverage and quirks

- **2021/2022 is score-only** (plus goal/card events and HT scores
  derivable from goal events). It can seed the goals fit and nothing else.
- **Stats era starts 2022/2023**: `total_shots`, `ShotsOnTarget`, `corners`,
  `yellow_cards`, `red_cards`, `BallPossesion`, `big_chance`, `fouls` on
  239/240 matches (238 in 2023/2024; one 2023/2024 match has corners but no
  yellow_cards). `touches_opp_box` is partial early (145/240 in 2022/2023,
  190/240 in 2023/2024, full from 2024/2025).
- **xG era starts inside the virgin**: `expected_goals` and shotmaps exist
  only in 2025/2026 and 2026/2027. Consequence: the goals model is
  goals-only (X1 dropped), and X3/X4/X6 have no dev-era data.
- **Period splits** (`stats.Periods.FirstHalf/SecondHalf`): 60 matches in
  2022/2023, near-complete from 2023/2024. A legitimate halves source
  exists for every market (goal events give HT goals in all eras; split
  stats give SOT/corners/total shots/yellows from the split era).
- **Referee** (`matchFacts.infoBox.Referee.text`): sparse in the dev era
  (82/240, 69/240, 62/210) and **collapses to 13/240 in the virgin
  2025/2026**. Combined with its failed reliability (Step 3: split-half
  r = 0.08), X8 is dropped.
- **Stats-card level shift in the seed season**: stats-feed yellows average
  2.23/match in 2022/2023 vs 3.75 in both scored dev seasons and 3.30 in
  the virgin — a recording-level shift between the first stats season and
  the rest (the same shape as TH's). 2022/2023 is seed/warm-up only and
  never scored; the walk-forward re-fits state continuously. No rescaling.

## The cards artefact — present, era-flipped, and the virgin is flipped too

Checked first, per programme rule (stats-feed yellow mean vs event-unified
yellow mean per match; exact agreement = both teams' counts equal):

| Season | Stats mean | Event-unified mean | Exact agreement (team-match) | Plain "Yellow" events |
|---|---|---|---|---|
| 2022/2023 | 2.230 | 0.054 | 0.410 | 0 |
| 2023/2024 | 3.747 | 0.051 | 0.156 | 0 |
| 2024/2025 | 3.748 | 0.057 | 0.124 | 0 |
| 2025/2026 (virgin) | 3.300 | 0.054 | 0.169 | 0 |
| 2026/2027 | 3.205 | 3.370 | 0.952 | 241 |

In the dev era AND in the virgin the **event feed is the broken one**: it
publishes NO plain "Yellow" card events at all in 2022/2023–2025/2026
(only Red and YellowRed events). An event-unified target would have mean
≈0.05 yellows/match — not a cards target. Full yellow events exist only
in 2021/2022 (211, a score-only season with no stats target) and in the
confirmatory 2026/2027, where the classic direction appears (stats 3.205
vs unified 3.370/match; exact agreement 95.2%).

**Frozen consequence (recorded in PREPROCESSING and the cards prereg):**
the cards target is the **stats-feed `yellow_cards`** in dev AND virgin —
the only target that exists in both windows. Unlike TH, no virgin
event-unified sensitivity is possible here: the unified count does not
exist in the virgin either. Recorded plainly; the gate is on the stats
target throughout.
