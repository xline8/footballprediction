# Step 3/4 — EDA & Visualization: CN-LeagueOne

Evidence from `analysis/eda.py` → `eda_summary.json`, charts in
`analysis/charts/` (levels_by_season, coverage_by_season,
halves_constants, trait_reliability). Virgin-season (2025) levels are
inventory only — they were NOT used to choose any line, arm, or
window; line selection uses the dev scored window 2022–2024 only.

- **F1 Levels by season (per match)**: goals 2.71 / 2.61 / 2.26 /
  2.48 (dev 2021–2024), 2.61 virgin, 2.69 reserve — no level break
  anywhere; 2023 is the low season (2.26) and the level recovered
  after it. Home-win rate 0.39 / 0.43 / 0.43 / 0.41 (dev); draw
  0.24 / 0.20 / 0.30 / 0.33; OU2.5 over-rate 0.50 / 0.51 / 0.38 /
  0.43 (dev scored window 2022–2024: 0.445). SOT, corners,
  total shots, stats yellows: **null in every season** — the stats
  feed does not exist in this league at any point, so S/C/K/T have
  no target, no reliability, no halves, no line. This is the
  scores-only verdict, measured, not assumed (brief confirmed).
- **F2 Trait reliability (split-half r, dev era, n=33 teams)**:
  goals-for 0.730, goals-against 0.811 — team scoring and conceding
  traits are strongly reliable (the strongest of the scores-only
  precedents), so Dixon-Coles ratings are meaningful here.
  Season-to-season correlations of team means decay fast for attack
  (GF r 0.82 in 2021–2022, 0.40 in 2022–2023, 0.13 in 2023–2024)
  while defence carries better (GA r 0.89 / 0.59 / 0.34): attack
  traits churn hard across seasons in this league — the ratings are
  re-fitted expanding, never carried frozen across seasons, and the
  dev gate decides whether the churn is survivable.
- **F3 Halves shares (dev era, frozen as config constants)**:
  goals **0.4493** (event times, dev era 2021–2024, 2,760 goals,
  1,000 matches with events; awarded matches excluded).
  Presentation only, never fitted on virgin data. SOT /
  corners / total shots / stats yellows halves: **null** — no period
  splits exist in any season. Event-yellows 1H share 0.1231 is
  computed but is NOT a frozen constant — the underlying count is
  YellowRed-only (see F5) and there is no K market.
- **F4 Entrant transitions (dev era)**: 15 transitions, mean GF
  diff +0.095, GA diff −0.034 vs league team mean, median GF
  −0.042 / GA −0.065, signs mixed per team (GF diff −0.37…+1.09;
  GA diff −0.60…+0.67). The means are pulled by two strong
  outliers (Qingdao Hainiu +0.96 GF in 2022, Yunnan Yukun +1.09 GF
  in 2024); the median entrant sits slightly below league average
  on both sides. **No systematic entrant tilt** (contrast FI:
  −0.358 / +0.263 with consistent signs) — the X2 entrant offset
  is therefore dropped pre-fitting (FEATURES.md), same decision as
  NO (whose means were +0.057 / +0.035) and CH.
- **F5 Cards feed verdict**: the stats feed carries no yellow_cards
  key in any season, and referee coverage is 0% in every season, so
  no X8 referee arm exists. Worse than the NO precedent: the event
  feed carries plain Yellow events in **no season at all** (0 plain
  Yellows in 1,572 matches; only YellowRed 5/21/25/14 and Red
  55/51/46/41 in dev). There is therefore no yellows target of any
  kind in any season. K-CN is **not-buildable** (no target, no
  referee) — the strongest not-buildable case in the program so far.
- **F6 Line selection (dev over-rates, scored window 2022–2024,
  n=786)**: goals OU 1.5 → 0.728, **2.5 → 0.445**, 3.5 → 0.228.
  The closest-to-0.5 line is 2.5, and the frozen goals evaluation
  line is **OU 2.5**, the program standard frozen identically in
  the FI/CH/IL/NO goals preregs (gates must stay comparable across
  leagues). Ladders ±1 around the primary are reported by the
  engine; gates sit at OU 2.5. Home-win rate in the scored window:
  0.422; draw: 0.274. Dev scored mean team goals 1.2335/match
  (1,939 goals / 786 matches / 2).

## Window consequence

Goals has a full dev: warm-up 2021 + scored 2022–2024 (n=786),
season-blocked expanding fit. S/C/K/T have no dev window at all —
not a thin dev, a nonexistent one. The split was not moved to
manufacture a window for them.
