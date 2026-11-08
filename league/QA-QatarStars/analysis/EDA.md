# Step 3/4 — EDA & Visualization: QA-QatarStars

Evidence from `analysis/eda.py` → `eda_summary.json`, charts in
`analysis/charts/` (levels_by_season, coverage_by_season,
halves_constants, trait_reliability). Virgin-season (2025/2026) levels
appear in the inventory table only — they were NOT used to choose any
line, arm, or window. Line selection, halves constants, trait
reliability, and entrant transitions use dev-era (≤ 2024/2025) data only.

- **F1 Levels by season (per match)**: goals 3.212 / 3.045 / 3.652 /
  3.348 in 2021/2022–2024/2025 (dev scored window 2022/2023–2024/2025
  mean 3.348 — a high-scoring league, no era break in the goals
  target). Stats-era levels exist only in 2025/2026–2026/2027
  (inventory only): SOT 9.69 / 11.00, corners 9.56 / 10.24, total
  shots 26.24 / 29.37, stats yellows 4.63 / 4.09. The single 2024/2025
  stats match is not reported as a season level (n=1).
- **F2 Trait reliability (split-half r, dev era)**: goals-for **0.796**
  (n=15 teams) — the goals trait is reliable enough to rate. SOT,
  corners, shots, yellows, possession: **not measurable on dev** — the
  targets are absent in every dev season, so no split-half correlation
  exists to compute. The count candidates are not-buildable on trait
  grounds as well as on window grounds.
- **F3 Halves shares (dev era, frozen as config constants)**: goals
  **0.4385** (event times, 1,749 goals, 505 matches; per-season shares
  0.4363 / 0.4204 / 0.4315 / 0.4649, stable). SOT / corners /
  total shots / yellows 1H shares are **NOT computable on dev**: 0
  matches with FirstHalf/SecondHalf splits in dev (the single 2024/2025
  stats match has All only). No halves constant exists for any count
  market, and none is invented — the config freezes only
  `goals_1h_share`. Event-time 1H yellows are likewise not derived:
  dev card events are YellowRed only (second yellows), the wrong
  target.
- **F4 Entrant transitions (dev era)**: 4 transitions, mean GF diff
  **−0.356**, GA diff **+0.360** vs league team mean. GF is negative in
  4 of 4, GA positive in **4 of 4** (Al Markhiya −0.159/+0.159,
  Muaither SC −0.280/+0.765, Al-Khor −0.720/+0.235, Al-Shahaniya
  −0.265/+0.280). The tilt is in the same direction as FI (−0.210/
  +0.159) and EC (−0.121/+0.263), and larger — a systematic entrant
  weakness. The X2 entrant offset is therefore **adopted for G-QA**
  (FEATURES.md / MODEL_DESIGN.md). Note Al-Khor's GF outlier (−0.720,
  a weak returning side) — the arm is a shrinkage-style offset, not a
  hard penalty; with only 4 transitions the offset is noisier than
  EC's 6, which is recorded in the prereg.
- **F5 Cards feed verdict**: the dev event feed carries zero plain
  Yellow events (2021/2022–2024/2025: Red 83, YellowRed 50, Yellow 0);
  the stats feed carries yellows only from 2025/2026. There is no cards
  target in any dev season under either source. K-QA is not-buildable
  under the frozen split. In 2025/2026 the two feeds agree exactly in
  only 25.8% of matches (mean stats − events +3.22/match) — a
  descriptive check only, and the gap is structural (events count
  reds/second yellows only).
- **F6 Line selection (dev over-rates, scored window 2022/2023–
  2024/2025, n=396)**: goals OU over-rates 1.5: 0.828, 2.5: **0.664**,
  3.5: 0.424. The over-rate closest to 0.5 is 3.5, but the frozen gate
  line stays **OU 2.5** per the program standard (FI/CH/EC/DK all gate
  on OU 2.5); the 0.664 over-rate is recorded as the league's
  high-scoring character, not a reason to move the line. Home win rate
  0.4066, draw rate 0.1869 in the same window. SOT / corners / total
  shots / yellows lines are null: no dev window exists to select a
  line on.
- **Window consequence (the central finding)**: the stats era starts
  in 2025/2026, i.e. in the virgin season itself. Stats markets (S/C/K/T)
  have **zero** warm-up seasons and **zero** scored dev seasons before
  the virgin — not a thin dev, no dev at all. The frozen split
  (dev ≤ 2024/2025, virgin 2025/2026, 2026/2027 untouched reserve) is
  NOT moved to manufacture one: re-splitting after seeing the era break
  would be post-hoc window shopping, and the gates decide on the frozen
  split. S/C/K/T verdicts at Phase 6 are therefore **not-buildable**,
  recorded pre-fitting. Only G-QA proceeds to Phase 3/4, with warm-up
  2021/2022 and scored dev 2022/2023–2024/2025 (n=396).
