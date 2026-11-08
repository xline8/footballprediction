# Step 3/4 — EDA & Visualization: IL-LigatHaAl

Evidence from `analysis/eda.py` → `eda_summary.json`, charts in
`analysis/charts/` (levels_by_season, coverage_by_season,
halves_constants, trait_reliability). Virgin-season (2025/2026) levels
appear in the inventory table only — they were NOT used to choose any
line, arm, or window. Line selection, halves constants, trait
reliability, and entrant transitions use dev-era (≤ 2024/2025) data only.

- **F1 Levels by season (per match)**: goals 2.471 / 2.642 / 2.542 /
  2.783 in 2021/2022–2024/2025 (dev scored window 2022/2023–2024/2025
  mean 2.656). The goals target itself is rising within dev (+0.31
  from the first to the last dev season) and rises further in the
  virgin (2.967) — a calibration risk flagged in DATA_UNDERSTANDING,
  not a reason to move any window. Stats-era levels exist only in
  2025/2026–2026/2027 (inventory only): SOT 9.10 / 9.39, corners
  9.26 / 9.43, total shots 26.03 / 28.42, stats yellows 4.78 / 4.72.
- **F2 Trait reliability (split-half r, dev era)**: goals-for **0.86**
  (n=18 teams) — the goals trait is reliable enough to rate. SOT,
  corners, shots, yellows, possession: **not measurable on dev** — the
  targets are absent in every dev season, so no split-half correlation
  exists to compute. The count candidates are not-buildable on trait
  grounds as well as on window grounds.
- **F3 Halves shares (dev era, frozen as config constants)**: goals
  **0.4497** (event times, 2,493 goals, 902 matches, awarded matches
  excluded — their event goals do not sum to the awarded FT score).
  SOT / corners / total shots / yellows 1H shares are **NOT computable
  on dev**: 0 matches with FirstHalf/SecondHalf splits in dev. No
  halves constant exists for any count market, and none is invented —
  the config freezes only `goals_1h_share`. Event-time 1H yellows are
  likewise not derived: dev card events are YellowRed only (second
  yellows), the wrong target.
- **F4 Entrant transitions (dev era)**: 6 transitions, mean GF diff
  **−0.358**, GA diff **+0.263** vs league team mean. GF is negative in
  5 of 6, GA positive in 5 of 6 (Sektzia Nes Tziona −0.381/+0.376,
  Maccabi Bnei Raina −0.351/+0.316, Maccabi Petach Tikva +0.063/+0.456,
  Hapoel Petah Tikva −0.513/+0.275, Ironi Tiberias −0.543/−0.028,
  Hapoel Ironi Kiryat Shmona −0.422/+0.184). The tilt is in the same
  direction as FI (−0.210/+0.159, adopted there) and EC (−0.121/+0.263,
  adopted there), and larger on the attack side. The X2 entrant offset
  is therefore **adopted for G-IL** (FEATURES.md / MODEL_DESIGN.md).
  Note the one GF outlier (Maccabi Petach Tikva +0.063, a strong
  promoted side) and the one GA exception (Ironi Tiberias −0.028) —
  the arm is a shrinkage-style offset, not a hard penalty.
- **F5 Cards feed verdict**: the dev event feed carries zero plain
  Yellow events (2021/2022–2024/2025: Red 185, YellowRed 98, Yellow
  0); the stats feed carries yellows only from 2025/2026. There is no
  cards target in any dev season under either source. K-IL is
  not-buildable under the frozen split. In 2025/2026 the two feeds
  agree exactly in 68.6% of matches (mean stats − events −0.53/match,
  events counting more — largely mechanical: the event count adds
  YellowRed on top of plain Yellows while the stats feed books a
  second yellow as a red) — a descriptive check only.
- **F6 Line selection (dev over-rates closest to 0.5)**: goals OU
  **2.5** (over-rates 1.5: 0.757, 2.5: **0.488**, 3.5: 0.263; dev scored
  window 2022/2023–2024/2025, n=720). Home win rate 0.3944, draw rate
  0.2556 in the same window. SOT / corners / total shots / yellows
  lines are null: no dev window exists to select a line on.
- **Window consequence (the central finding)**: the stats era starts
  in 2025/2026, i.e. in the virgin season itself. Stats markets
  (S/C/K/T) have **zero** warm-up seasons and **zero** scored dev
  seasons before the virgin — not a thin dev, no dev at all. The frozen
  split (dev ≤ 2024/2025, virgin 2025/2026, 2026/2027 untouched
  reserve) is NOT moved to manufacture one: re-splitting after seeing
  the era break would be post-hoc window shopping, and the gates
  decide on the frozen split. S/C/K/T verdicts at Phase 6 are therefore
  **not-buildable**, recorded pre-fitting. Only G-IL proceeds to Phase
  3/4, with warm-up 2021/2022 and scored dev 2022/2023–2024/2025
  (n=720).
