# Step 3/4 — EDA & Visualization: NO-2Divisjon

Evidence from `analysis/eda.py` → `eda_summary.json`, charts in
`analysis/charts/` (levels_by_season, coverage_by_season,
halves_constants, trait_reliability). Virgin-season (2025) levels are
inventory only — they were NOT used to choose any line, arm, or
window; line selection uses the dev scored window 2022–2024 only.

- **F1 Levels by season (per match)**: goals 3.52 / 3.39 / 3.33 /
  3.45 (dev 2021–2024), 3.53 virgin, 3.45 reserve — stable, no level
  break anywhere. Home-win rate 0.50 / 0.51 / 0.46 / 0.48 (dev);
  draw 0.21 / 0.20 / 0.22 / 0.18; OU2.5 over-rate 0.67 / 0.62 /
  0.65 / 0.68 (dev scored window 2022–2024: 0.648). SOT, corners,
  total shots, stats yellows: **null in every season** — the stats
  feed does not exist in this league at any point, so S/C/K/T have
  no target, no reliability, no halves, no line. This is the
  scores-only verdict, measured, not assumed (brief confirmed).
- **F2 Trait reliability (split-half r, dev era, n=49 teams)**:
  goals-for 0.561, goals-against 0.618 — team scoring and conceding
  traits are reliable enough to rate (Dixon-Coles ratings are
  meaningful here). Season-to-season correlations of team means are
  weaker for attack (GF r 0.23–0.34 across adjacent dev seasons)
  than defence (GA r 0.58–0.76): attack carries poorly across
  seasons in this high-churn tier-3 league, defence carries better.
  Expect the expanding fit to lag attack churn — the dev gate decides.
- **F3 Halves shares (dev era, frozen as config constants)**:
  goals **0.4435** (event times, dev era 2021–2024, 4,893 goals,
  1,398 matches with events; awarded matches excluded — none in
  dev). Presentation only, never fitted on virgin data. SOT /
  corners / total shots / stats yellows halves: **null** — no period
  splits exist in any season. Event-yellows 1H share 0.2981 is
  computed (2024 only carries plain Yellows) but is NOT a frozen
  constant — there is no K market.
- **F4 Entrant transitions (dev era)**: 25 transitions, mean GF
  diff +0.057, GA diff +0.035 vs league team mean, signs mixed per
  team (GF diff −0.55…+1.18; GA diff −0.95…+1.14). The large positive
  outliers are relegated tier-2 clubs (Ull/Kisa +1.11 GF in 2022,
  Lyn +1.18 GF in 2023); promoted tier-4 clubs tilt the other way.
  **No systematic entrant tilt** (contrast FI: −0.358 / +0.263 with
  consistent signs) — the X2 entrant offset is therefore dropped
  pre-fitting (FEATURES.md), same decision as CH (whose means were
  −0.079 / −0.035). NO is tier 3, so its entrants mix relegated,
  promoted, and reserve-team clubs with no single direction.
- **F5 Cards feed verdict**: the stats feed carries no yellow_cards
  key in any season, and referee coverage is 0% in every season, so
  no X8 referee arm exists. The event feed carries plain Yellow
  events ONLY from 2024 onward (2021–2023: 0 plain Yellows; only
  Red 35/25/22 and YellowRed 24/15/13). There is therefore no
  consistent yellows target across the dev era: a K model would have
  no dev window in 2021–2023 and a one-season target in 2024. K-NO
  is **not-buildable** (target-definition break + no referee), same
  feasibility class as IL's K verdict. Event yellows in 2024–2026
  average 3.02 / 3.31 / 3.27 per match — recorded, not fitted.
- **F6 Line selection (dev over-rates, scored window 2022–2024,
  n=1,066)**: goals OU 1.5 → 0.843, **2.5 → 0.648**, 3.5 → 0.439.
  The closest-to-0.5 line is 3.5, but the frozen goals evaluation
  line is **OU 2.5**, the program standard frozen identically in
  the FI/CH/IL goals preregs (gates must stay comparable across
  leagues; the 3.5 observation is recorded here, not acted on).
  Ladders ±1 around the primary are reported by the engine; gates
  sit at OU 2.5. Home-win rate in the scored window: 0.484; draw:
  0.201.

## Window consequence

Goals has a full dev: warm-up 2021 + scored 2022–2024 (n=1,066),
season-blocked expanding fit. S/C/K/T have no dev window at all —
not a thin dev, a nonexistent one. The split was not moved to
manufacture a window for them.
