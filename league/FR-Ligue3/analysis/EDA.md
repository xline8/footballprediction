# Step 3/4 — EDA & Visualization: FR-Ligue3

Evidence from `analysis/eda.py` → `eda_summary.json`, charts in
`analysis/charts/` (levels_by_season, coverage_by_season,
halves_constants, trait_reliability). Virgin-season (2025/2026)
levels are inventory only — they were NOT used to choose any line,
arm, or window; line selection uses the dev scored window
2022/2023–2024/2025 only.

- **F1 Levels by season (per match)**: goals 2.503 / 2.503 / 2.546 /
  2.393 (dev 2021/2022–2024/2025), 2.423 virgin, 2.389 reserve —
  stable, no level break anywhere. Home-win rate 0.441 / 0.386 /
  0.451 / 0.408 (dev); draw 0.261 / 0.314 / 0.265 / 0.316; OU2.5
  over-rate 0.474 / 0.441 / 0.461 / 0.401 (dev scored window
  2022/2023–2024/2025: 0.4355). SOT, corners, total shots, stats
  yellows: **null in every season** — the stats feed does not exist
  in this league at any point, so S/C/K/T have no target, no
  reliability, no halves, no line. This is the scores-only verdict,
  measured, not assumed (brief confirmed).
- **F2 Trait reliability (split-half r, dev era, n=35 teams)**:
  goals-for 0.323, goals-against 0.309 — team scoring and conceding
  traits are only weakly reliable (much weaker than NO's 0.561 /
  0.618). Season-to-season correlations of team means are also
  weak and mixed: GF r 0.24 / 0.37 / 0.40, GA r 0.25 / 0.57 / −0.21
  across adjacent dev seasons. In this high-churn tier-3 league
  team traits carry poorly across seasons — expect the expanding
  fit to lag churn; the dev gate decides.
- **F3 Halves shares (dev era, frozen as config constants)**:
  goals **0.4618** (event times, dev era 2021/2022–2024/2025, 2,947
  goals, 1,148 matches with events; awarded matches excluded).
  Presentation only, never fitted on virgin data. SOT / corners /
  total shots / stats yellows halves: **null** — no period splits
  exist in any season. Event-yellows 1H share 0.3580 is computed
  (2023/2024 onward only carries plain Yellows) but is NOT a frozen
  constant — there is no K market.
- **F4 Entrant transitions (dev era)**: 21 transitions, mean GF
  diff −0.010, GA diff −0.011 vs league team mean, signs mixed per
  team (GF diff −0.38…+0.43; GA diff −0.32…+0.24). **No systematic
  entrant tilt** (contrast FI: −0.358 / +0.263 with consistent
  signs) — the X2 entrant offset is therefore dropped pre-fitting
  (FEATURES.md), same decision as CH and NO. FR is tier 3, so its
  entrants mix relegated, promoted, and reserve-team clubs with no
  single direction.
- **F5 Cards feed verdict**: the stats feed carries no yellow_cards
  key in any season, and referee coverage is 0% in every season, so
  no X8 referee arm exists. The event feed carries plain Yellow
  events ONLY from 2023/2024 onward (2021/2022–2022/2023: 0 plain
  Yellows; only Red and YellowRed). There is therefore no consistent
  yellows target across the dev era: a K model would have no dev
  window in 2021/2022–2022/2023 and a two-season target from
  2023/2024. K-FR is **not-buildable** (target-definition break + no
  referee), same feasibility class as IL's and NO's K verdicts.
  Event yellows in 2023/2024–2025/2026 average 3.75 / 4.34 / 4.06
  per match — recorded, not fitted.
- **F6 Line selection (dev over-rates, scored window
  2022/2023–2024/2025, n=884)**: goals OU 1.5 → 0.709, **2.5 →
  0.4355**, 3.5 → 0.2353. The closest-to-0.5 line is 2.5, and the
  frozen goals evaluation line is **OU 2.5**, the program standard
  frozen identically in the FI/CH/IL/NO goals preregs (gates must
  stay comparable across leagues). Ladders ±1 around the primary are
  reported by the engine; gates sit at OU 2.5. Home-win rate in the
  scored window: 0.415; draw: 0.298.

## Window consequence

Goals has a full dev: warm-up 2021/2022 + scored 2022/2023–2024/2025
(n=884), season-blocked expanding fit. S/C/K/T have no dev window
at all — not a thin dev, a nonexistent one. The split was not moved
to manufacture a window for them.
