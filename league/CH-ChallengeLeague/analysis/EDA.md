# Step 3/4 — EDA & Visualization: CH-ChallengeLeague

Evidence from `analysis/eda.py` → `eda_summary.json`, charts in
`analysis/charts/` (levels_by_season, coverage_by_season,
halves_constants, trait_reliability). Virgin-season (2025/2026) levels
were NOT used to choose any line, arm, or window — line selection uses
dev windows only.

- **F1 Levels by season (per match)**: goals 3.25 / 3.13 / 2.87 / 3.00
  (dev seasons, stable); SOT 8.67 / 8.91; corners 9.99 / 8.49 (a real
  level drop between 2023/2024 and 2024/2025 — the calibration leg's
  problem, recorded not repaired); total shots 25.61 / 25.30 —
  **consistent across the stats era, no definition break** (unlike
  FI's thin/rich break: CH's stats feed simply starts in 2023/2024,
  already rich). Stats yellows 4.58 / 5.01.
- **F2 Trait reliability (split-half r, dev era)**: goals-for 0.80,
  SOT-for 0.71, possession 0.71, yellows-for 0.67, shots-for 0.63,
  corners-for 0.62. Every candidate's team trait is reliable enough to
  rate — the count candidates are buildable on trait grounds.
- **F3 Halves shares (dev era, frozen as config constants)**:
  goals 0.4409 (event times, 2,207 goals), SOT 0.4512, corners 0.4800,
  total shots 0.4467, yellows 0.3399 (last four from period splits,
  2023/2024–2024/2025, n=360 matches; goals from event times over the
  full dev era). Presentation only, never fitted on virgin data.
- **F4 Entrant transitions (dev era)**: 7 transitions, mean GF diff
  −0.079, GA diff −0.035 vs league team mean, mixed signs per team —
  **no systematic entrant tilt** (contrast FI: −0.210 / +0.159). The
  X2 entrant offset is therefore dropped pre-fitting (FEATURES.md);
  CH is tier 2, so its entrants mix relegated and promoted clubs.
- **F5 Cards feed verdict**: event yellows total just 85 across the
  whole dev era versus ~4.8/match in the stats feed — the event feed
  is not a cards source in this league (Step 1). K-CH runs on stats
  yellows, stats-era windows only.
- **F6 Line selection (dev over-rates closest to 0.5)**: goals OU
  **2.5** (0.578, dev 2022/23–2024/25); SOT **8.5** (0.533); corners
  **8.5** (0.467); total shots **26.5** (0.439); yellows **4.5**
  (0.606; 5.5 gives 0.383, so 4.5 is closest) — count-market rates
  from the dev scored window 2024/2025, n=180. Ladders ±1 around each
  primary are reported by the engines; gates sit at the primary.
- **Window consequence**: stats markets (S/C/K/T) have exactly one
  warm-up season (2023/2024) and one scored dev season (2024/2025)
  before the virgin — a thinner dev than FI's, a direct consequence of
  the feed starting in 2023/2024. The dev protocol is the program's
  per-match chronological walk-forward (predict-then-update), which
  uses all 180 warm-up matches as state before scoring; gates are
  unchanged and SEs are reported honestly.
