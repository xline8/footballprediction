# Step 3/4 — EDA & Visualization: BY-PremierLeague

Evidence from `analysis/eda.py` → `eda_summary.json`, charts in
`analysis/charts/` (levels_by_season, coverage_by_season,
halves_constants, trait_reliability). Virgin-season (2025) levels
are inventory only — they were NOT used to choose any line, arm, or
window; line selection uses the dev scored window 2022–2024 only.

- **F1 Levels by season (per match)**: goals 2.713 / 2.542 / 2.738 /
  2.346 (dev 2021–2024), 2.546 virgin, 2.603 reserve — no level
  break, but 2024 (2.346) is the lowest season and 2023 (2.738) the
  highest; the dev scored mean is 2.533. Home-win rate 0.425 /
  0.350 / 0.448 / 0.400 (dev); draw 0.254 / 0.296 / 0.214 / 0.275;
  OU2.5 over-rate 0.517 / 0.467 / 0.500 / 0.404 (dev scored window
  2022–2024: 0.4551). SOT, corners, total shots, stats yellows:
  **null in every season** — the stats feed does not exist in this
  league at any point, so S/C/K/T have no target, no reliability,
  no halves, no line. This is the scores-only verdict, measured,
  not assumed (brief confirmed).
- **F2 Trait reliability (split-half r, dev era, n=20 teams)**:
  goals-for 0.855, goals-against 0.947 — team scoring and conceding
  traits are STRONGLY reliable within the dev era (much stronger
  than FR's 0.323 / 0.309 or NO's 0.561 / 0.618). Season-to-season
  correlations of team means are moderate and positive: GF r 0.45
  / 0.25 / 0.31, GA r 0.63 / 0.28 / 0.70 across adjacent dev
  seasons (n=13 common teams each pair). In this stable 16-team
  top flight, team traits carry well across seasons — the
  expanding fit has something real to track; the dev gate decides.
- **F3 Halves shares (dev era, frozen as config constants)**:
  goals **0.4314** (event times, dev era 2021–2024, 2,348 goals,
  845 matches with events; awarded matches excluded). Lower than
  FR's 0.4618 — a league-specific constant, frozen as measured.
  Presentation only, never fitted on virgin data. SOT / corners /
  total shots / stats yellows halves: **null** — no period splits
  exist in any season. Event-yellows 1H share 0.1429 is computed
  (91 YellowRed events in dev, no plain Yellows anywhere) but is
  NOT a frozen constant — there is no K market.
- **F4 Entrant transitions (dev era)**: 8 transitions, mean GF
  diff −0.325, GA diff +0.426 vs league team mean — a LARGE,
  CONSISTENT entrant tilt: GF diff is negative in 8/8 transitions
  (−0.07…−0.67) and GA diff positive in 7/8 (−0.34…+1.16; only
  Vitebsk 2024 concedes below average). Entrants are promoted
  clubs that score ~0.33 fewer and concede ~0.43 more per match
  than the league mean in their first season. **The X2 entrant
  offset is therefore KEPT pre-fitting** (FEATURES.md) — the
  opposite decision to CH/NO/FR, where the tilt was ~0 and mixed.
  The clamped offsets are g_log −0.223 (= log 0.8) and c_log
  +0.223 (= log 1.25): the raw means (−0.325 / +0.426) hit the
  program clamp on both sides.
- **F5 Cards feed verdict**: the stats feed carries no yellow_cards
  key in any season, and referee coverage is 0% in every season, so
  no X8 referee arm exists. The event feed carries **zero plain
  Yellow events in any season** (2021–2026: only YellowRed and Red
  cards; YellowRed totals 31 / 30 / 14 / 17 / 2 / 3, Red totals
  40 / 42 / 30 / 32 / 31 / 26). There is therefore NO yellows
  target at all in this league — not a definition break across
  eras, a total absence. K-BY is **not-buildable** (no target +
  no referee), the strongest form of the K verdict. Event
  "yellows" (YellowRed only) average 0.15 / 0.14 / 0.07 / 0.08 /
  0.01 / 0.01 per match — recorded, not fitted.
- **F6 Line selection (dev over-rates, scored window 2022–2024,
  n=690)**: goals OU 1.5 → 0.700, **2.5 → 0.4551**, 3.5 → 0.2638.
  The closest-to-0.5 line is 2.5, and the frozen goals evaluation
  line is **OU 2.5**, the program standard frozen identically in
  the FI/CH/IL/NO/FR goals preregs (gates must stay comparable
  across leagues). Ladders ±1 around the primary are reported by
  the engine; gates sit at OU 2.5. Home-win rate in the scored
  window: 0.397; draw: 0.264.

## Window consequence

Goals has a full dev: warm-up 2021 + scored 2022–2024 (n=690),
season-blocked expanding fit. S/C/K/T have no dev window at all —
not a thin dev, a nonexistent one. The split was not moved to
manufacture a window for them.
