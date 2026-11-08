# Step 3/4 — EDA & Visualization: SG-PremierLeague

Evidence from `analysis/eda.py` → `eda_summary.json`, charts in
`analysis/charts/` (levels_by_season, coverage_by_season,
halves_constants, trait_reliability). Virgin-season (2025/2026)
levels are inventory only — they were NOT used to choose any line,
arm, or window; line selection uses the dev scored window
2022 + 2023 + 2024/2025 only.

- **F1 Levels by season (per match)**: goals 3.976 / 4.518 /
  4.185 / 4.257 (dev 2021–2024/2025), 3.607 virgin, 3.478
  reserve — the highest-scoring league in the program so far,
  with no level break inside the dev era (range 3.98–4.52).
  Home-win rate 0.393 / 0.446 / 0.426 / 0.389 (dev); draw 0.238 /
  0.205 / 0.120 / 0.222 (low — Singapore draws are rare); OU2.5
  over-rate 0.786 / 0.768 / 0.769 / 0.785 (dev scored window:
  0.7747). SOT, corners, total shots, stats yellows: **null in
  every season** — the stats feed does not exist in this league
  at any point, so S/C/K/T have no target, no reliability, no
  halves, no line. This is the scores-only verdict, measured,
  not assumed (brief confirmed).
- **F2 Trait reliability (split-half r, dev era, n=9 teams)**:
  goals-for 0.881, goals-against 0.869 — team scoring and
  conceding traits are STRONGLY reliable within the dev era.
  Season-to-season correlations of team means are positive:
  GF r 0.956 / 0.767 / 0.361, GA r 0.589 / 0.827 / 0.646 across
  adjacent dev seasons (8–9 common teams per pair; the small
  league means few teams, so single-season correlations are
  noisy, but the split-half evidence is decisive). The expanding
  fit has real signal to track; the dev gate decides.
- **F3 Halves shares (dev era, frozen as config constants)**:
  goals **0.4404** (event times, dev era 2021–2024/2025, 1,905
  goals, 440 matches with events; no awarded matches exist).
  Because all 12 no-event matches are 0-0, the event-goal total
  equals the full dev goal total — the constant is measured on
  the complete dev goal population. Presentation only, never
  fitted on virgin data. SOT / corners / total shots / stats
  yellows halves: **null** — no period splits exist in any
  season. Event-yellows 1H share 0.125 is computed (32 YellowRed
  events in dev, no plain Yellows anywhere) but is NOT a frozen
  constant — there is no K market.
- **F4 Entrant transitions (dev era)**: exactly **1** transition
  — Brunei DPMM returning in 2023 (24 matches, GF diff −0.468,
  GA diff −0.301 vs league team mean). One transition is below
  the program's minimum evidence (the X2 rule itself returns
  offset 0 with fewer than 3 completed transitions), and its GA
  sign (an entrant conceding LESS than average — DPMM is a
  strong guest club, not a promoted side) contradicts the
  entrant pattern anyway. **The X2 entrant offset is therefore
  DROPPED pre-fitting** (FEATURES.md) — the same decision as
  CH/NO/SE, the opposite of BY/FI where 8 consistent transitions
  justified keeping it. G-SG arms are Gate Zero + SHRINK only.
- **F5 Cards feed verdict**: the stats feed carries no
  yellow_cards key in any season, and referee coverage is 0% in
  every dev season (and in the virgin), so no X8 referee arm
  exists. The event feed carries **zero plain Yellow events in
  any season** (2021–2026/2027: only YellowRed and Red cards;
  YellowRed totals 8 / 5 / 13 / 6 / 1 / 3, Red totals 11 / 14 /
  35 / 31 / 26 / 10). There is therefore NO yellows target at
  all in this league — not a definition break across eras, a
  total absence. K-SG is **not-buildable** (no target + no
  referee), the strongest form of the K verdict — identical in
  structure to K-BY. Event "yellows" (YellowRed only) average
  0.098 / 0.045 / 0.120 / 0.043 per match in the dev era —
  recorded, not fitted.
- **F6 Line selection (dev over-rates, scored window 2022 +
  2023 + 2024/2025, n=364)**: goals OU 1.5 → 0.9176, **2.5 →
  0.7747**, 3.5 → 0.6181. In this high-scoring league the
  closest-to-0.5 line is 3.5; the frozen goals evaluation line
  is nevertheless **OU 2.5**, the program standard frozen
  identically in every goals prereg in the program (gates must
  stay comparable across leagues). Ladders ±1 around the
  primary are reported by the engine; gates sit at OU 2.5.
  Home-win rate in the scored window: 0.4176; draw: 0.1868.
  Dev scored mean team goals 2.158/match (1,571 goals / 364
  matches / 2).

## Window consequence

Goals has a full dev: warm-up 2021 + scored 2022, 2023,
2024/2025 (n=364), season-blocked expanding fit. S/C/K/T have no
dev window at all — not a thin dev, a nonexistent one. The split
was not moved to manufacture a window for them.
