# Step 3/4 — EDA & Visualization: IN-IndianFootballLeague

Evidence from `analysis/eda.py` → `eda_summary.json`, charts in
`analysis/charts/` (levels_by_season, coverage_by_season,
halves_constants, trait_reliability). Virgin-season (2025/2026)
levels are inventory only — they were NOT used to choose any line,
arm, or window; line selection uses the dev scored window
2022/2023–2024/2025 only.

- **F1 Levels by season (per match)**: goals 2.579 / 2.727 / 3.331 /
  3.182 (dev 2021/2022–2024/2025), 3.045 virgin, 2.700 reserve. The
  level ROSE across the dev era: the two most recent dev seasons
  (3.331, 3.182) are the two highest, so the expanding fit chases a
  rising level — a known calibration risk, recorded for the prereg.
  Dev scored mean is 3.093. Home-win rate 0.351 / 0.515 / 0.403 /
  0.424 (dev); draw 0.272 / 0.220 / 0.234 / 0.265; OU2.5 over-rate
  0.483 / 0.515 / 0.610 / 0.583 (dev scored window: 0.5718). SOT,
  corners, total shots, stats yellows: **null in every season** —
  the stats feed does not exist in this league at any point, so
  S/C/K/T have no target, no reliability, no halves, no line. This
  is the scores-only verdict, measured, not assumed (brief
  confirmed).
- **F2 Trait reliability (split-half r, dev era, n=19 teams)**:
  goals-for 0.608, goals-against 0.462 — team traits are MODERATELY
  reliable within the dev era (weaker than BY's 0.855 / 0.947,
  stronger than FR's 0.323 / 0.309). Season-to-season correlations
  of team means are weak-to-moderate and mostly positive: GF r
  0.41 / 0.36 / 0.26, GA r −0.02 / 0.26 / 0.23 across adjacent dev
  seasons (n=12 / 9 / 10 common teams). Team identity is fluid in
  this tier-2 league (promotion/relegation churn, 24 ids over 6
  seasons for 10–13 slots), so the expanding fit has real but
  modest signal to track; the dev gate decides.
- **F3 Halves shares (dev era, frozen as config constants)**:
  goals **0.4387** (event times, dev era 2021/2022–2024/2025,
  1,575 goals, 497 matches with events; awarded matches excluded).
  Presentation only, never fitted on virgin data. SOT / corners /
  total shots / stats yellows halves: **null** — no period splits
  exist in any season. Event-yellows 1H share 0.0625 is computed
  (48 YellowRed events in dev, no plain Yellows in dev) but is NOT
  a frozen constant — there is no K market.
- **F4 Entrant transitions (dev era)**: 6 transitions (none in
  2022/2023; Delhi FC, Shillong Lajong, Inter Kashi, Namdhari FC in
  2023/2024; SC Bengaluru, Dempo SC in 2024/2025), mean GF diff
  −0.110, GA diff +0.025 vs league team mean — signs MIXED: GF
  diff negative in 3/6 (+0.168, −0.166, +0.293, −0.457, −0.500,
  0.000), GA diff positive in 3/6, negative in 2/6, ~zero in 1/6.
  The GA tilt is essentially zero (+0.025). **The X2 entrant
  offset is therefore DROPPED pre-fitting** (FEATURES.md) — the
  same decision as CH/NO/FR/SE, where the tilt was ~0 and mixed,
  and the opposite of FI/BY, where FI adopted on 8 consistent
  transitions (−0.210 / +0.159) and BY on 8 near-unanimous ones
  (−0.325 / +0.426). The G-IN arms are Gate Zero + SHRINK only.
- **F5 Cards feed verdict**: the stats feed carries no yellow_cards
  key in any season. The event feed carries **zero plain Yellow
  events in every dev season AND in the virgin** (2021/2022–
  2025/2026: only YellowRed and Red; YellowRed totals 12 / 13 / 16
  / 7 / 0, Red totals 24 / 24 / 27 / 31 / 15). Plain Yellows appear
  ONLY in the untouched reserve (27 in 2026/2027) — a
  target-definition break that sits entirely outside the modelled
  eras, so no consistent yellows target exists in dev. Referee
  coverage is real in dev (453/496, 91.3%) but collapses in the
  virgin (4/66, 6.1%), so no X8 referee arm could ship anyway.
  K-IN is **not-buildable** (no target in dev). Event "yellows"
  (YellowRed only) average 0.114 / 0.104 / 0.110 / 0.056 / 0.000
  per match — recorded, not fitted.
- **F6 Line selection (dev over-rates, scored window
  2022/2023–2024/2025, n=418)**: goals OU 1.5 → 0.7871, **2.5 →
  0.5718**, 3.5 → 0.3565. The closest-to-0.5 line is 2.5, and the
  frozen goals evaluation line is **OU 2.5**, the program standard
  frozen identically in the FI/CH/IL/NO/FR/BY goals preregs (gates
  must stay comparable across leagues). Ladders ±1 around the
  primary are reported by the engine; gates sit at OU 2.5.
  Home-win rate in the scored window: 0.4450; draw: 0.2392.

## Window consequence

Goals has a full dev: warm-up 2021/2022 + scored
2022/2023–2024/2025 (n=418), season-blocked expanding fit.
S/C/K/T have no dev window at all — not a thin dev, a nonexistent
one. The split was not moved to manufacture a window for them.
The virgin (2025/2026, n=66) is small, so its sampling-noise band
is wide; the gate is applied as written, not softened (BRIEF).
