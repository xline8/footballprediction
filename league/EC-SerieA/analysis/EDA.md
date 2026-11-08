# Step 3/4 — EDA & Visualization: EC-SerieA

Evidence from `analysis/eda.py` → `eda_summary.json`, charts in
`analysis/charts/` (levels_by_season, coverage_by_season,
halves_constants, trait_reliability). Virgin-season (2025) levels
appear in the inventory table only — they were NOT used to choose any
line, arm, or window. Line selection, halves constants, trait
reliability, and entrant transitions use dev-era (≤ 2024) data only.

- **F1 Levels by season (per match)**: goals 2.719 / 2.426 / 2.471 /
  2.628 in 2021–2024 (dev scored window 2022–2024 mean 2.508; stable,
  no era break in the goals target). Stats-era levels exist only in
  2025–2026 (inventory only): SOT 8.50 / 8.27, corners 9.62 / 9.33,
  total shots 25.58 / 26.41, stats yellows 4.06 / 4.25. The single 2024
  stats match is not reported as a season level (n=1).
- **F2 Trait reliability (split-half r, dev era)**: goals-for **0.75**
  (n=21 teams) — the goals trait is reliable enough to rate. SOT,
  corners, shots, yellows, possession: **not measurable on dev** — the
  targets are absent in every dev season, so no split-half correlation
  exists to compute. The count candidates are not-buildable on trait
  grounds as well as on window grounds.
- **F3 Halves shares (dev era, frozen as config constants)**: goals
  **0.4616** (event times, 2,474 goals, 902 matches). SOT / corners /
  total shots / yellows 1H shares are **NOT computable on dev**: 0
  matches with FirstHalf/SecondHalf splits in dev (the single 2024
  stats match has All only). No halves constant exists for any count
  market, and none is invented — the config freezes only
  `goals_1h_share`. Event-time 1H yellows are likewise not derived:
  dev card events are YellowRed only (second yellows), the wrong
  target.
- **F4 Entrant transitions (dev era)**: 6 transitions, mean GF diff
  **−0.121**, GA diff **+0.263** vs league team mean. GF is negative in
  5 of 6, GA positive in **6 of 6** (Cumbaya −0.313/+0.087, Gualaceo
  −0.279/+0.321, El Nacional +0.664/+0.231, Libertad −0.169/+0.231,
  CSD Macara −0.447/+0.019, Imbabura −0.181/+0.686). The tilt is in the
  same direction and of comparable size to FI (−0.210/+0.159, adopted
  there) and unlike CH (−0.079/−0.035, dropped there). The X2 entrant
  offset is therefore **adopted for G-EC** (FEATURES.md / MODEL_DESIGN.md).
  Note the one GF outlier (El Nacional +0.664, a strong promoted side)
  — the arm is a shrinkage-style offset, not a hard penalty.
- **F5 Cards feed verdict**: the dev event feed carries zero plain
  Yellow events (2021–2024: Red 240, YellowRed 170, Yellow 0); the
  stats feed carries yellows only from 2025. There is no cards target
  in any dev season under either source. K-EC is not-buildable under
  the frozen split. In 2025 the two feeds agree exactly in 80.1% of
  matches (mean stats − events −0.36/match) — a descriptive check only.
- **F6 Line selection (dev over-rates closest to 0.5)**: goals OU
  **2.5** (over-rates 1.5: 0.712, 2.5: **0.464**, 3.5: 0.251; dev scored
  window 2022–2024, n=726). Home win rate 0.4766, draw rate 0.2824 in
  the same window. SOT / corners / total shots / yellows lines are
  null: no dev window exists to select a line on.
- **Window consequence (the central finding)**: the stats era starts
  in 2025, i.e. in the virgin season itself. Stats markets (S/C/K/T)
  have **zero** warm-up seasons and **zero** scored dev seasons before
  the virgin — not a thin dev, no dev at all. The frozen split
  (dev ≤ 2024, virgin 2025, 2026 untouched reserve) is NOT moved to
  manufacture one: re-splitting after seeing the era break would be
  post-hoc window shopping, and the gates decide on the frozen split.
  S/C/K/T verdicts at Phase 6 are therefore **not-buildable**, recorded
  pre-fitting. Only G-EC proceeds to Phase 3/4, with warm-up 2021 and
  scored dev 2022–2024 (n=726).
