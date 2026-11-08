# Step 3/4 — EDA & Visualization: MD-NationalDivision

Evidence from `analysis/eda.py` → `eda_summary.json`, charts in
`analysis/charts/` (levels_by_season, coverage_by_season,
halves_constants, trait_reliability). Virgin-season (2025/2026)
levels are inventory only — they were NOT used to choose any line,
arm, or window; line selection uses the dev scored window
2022/2023–2024/2025 only.

- **F1 Levels by season (per match)**: goals 3.063 / 2.128 / 2.953 /
  2.965 (dev 2021/2022–2024/2025), 2.947 virgin, 2.986 reserve —
  the 2022/2023 season (2.128) is a deep level dip against both
  neighbours; the dev scored mean is 2.682. Home-win rate dev:
  0.411 / 0.407 / 0.512 / 0.453; draw 0.161 / 0.279 / 0.186 /
  0.256; OU2.5 over-rate dev scored window: 0.488. SOT, corners,
  total shots, stats yellows: **null in every season** — the stats
  feed does not exist in this league at any point (0/556), so
  S/C/K/T have no target, no reliability, no halves, no line.
  This is the scores-only verdict, measured, not assumed (BRIEF
  confirmed).
- **F2 Trait reliability (split-half r, dev era, n=10 teams)**:
  goals-for 0.885, goals-against 0.877 — team traits are STRONGLY
  reliable (a stable 8-team league; the same clubs recur).
  Season-to-season correlations of team means are positive and
  mostly strong: GF r 0.80 / 0.81 / 0.47, GA r 0.91 / 0.48 / 0.65
  across adjacent dev seasons. The expanding fit has real signal
  to track; the dev gate decides.
- **F3 Halves shares (dev era, frozen as config constants)**:
  goals **0.4388** (event times, dev era 2021/2022–2024/2025,
  awarded excluded, 1,005 goals in 336 matches with events).
  Presentation only, never fitted on virgin data. SOT / corners /
  total shots / stats yellows halves: **null** — no period splits
  exist in any season. Event-yellows halves are not computed as a
  constant — there is no K market (F5).
- **F4 Entrant transitions (dev era)**: only **3 transitions**
  (Dacia Buiucani 2022/2023; CF Sparta Selemet + FC Floresti
  2023/2024; none into 2024/2025). Mean GF diff −0.363 (negative
  3/3), mean GA diff +0.780 (positive 2/3; only Dacia Buiucani
  conceded below the league mean). The tilt direction matches the
  program pattern and both raw means exceed the clamp, giving
  g_log −0.223 / c_log +0.223. With the frozen rule (offset from
  completed transitions only, <3 → 0), X2 is **KEPT** as an arm —
  but note it is numerically inert on the dev scored window: the
  2022/2023 entrant has 0 prior transitions, the 2023/2024
  entrants have 1 (<3 → offset 0), and 2024/2025 has no entrants.
  X2 can only differ from SHRINK on the virgin season, if it is
  ever read.
- **F5 Cards feed verdict**: the stats feed carries no
  yellow_cards key in any season and referee coverage is 0% in
  every season (no X8 arm). The event feed carries **zero plain
  Yellow events in any season** (YellowRed totals by season
  9 / 4 / 5 / 5 / 1 / 1; Red totals 13 / 8 / 11 / 18 / 21 / 10).
  There is NO yellows target at all in this league — a total
  absence, not a definition break. K-MD is **not-buildable**.
- **F6 Line selection (dev over-rates, scored window
  2022/2023–2024/2025, n=258)**: goals OU 1.5 → 0.7481, **2.5 →
  0.4884**, 3.5 → 0.2829. The closest-to-0.5 line is 2.5, and the
  frozen goals evaluation line is **OU 2.5**, the program standard
  (gates stay comparable across leagues). Home-win rate in the
  scored window: 0.4574; draw: 0.2403. Dev scored mean team
  goals: 1.3411/match (692 goals / 258 matches / 2).

## Window consequence

Goals has a full dev: warm-up 2021/2022 + scored
2022/2023–2024/2025 (n=258), season-blocked expanding fit.
S/C/K/T have no dev window at all — not a thin dev, a nonexistent
one. The split was not moved to manufacture a window for them.
