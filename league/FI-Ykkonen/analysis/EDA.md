# Step 3/4 — EDA & Visualization: FI-Ykkonen

Evidence from `analysis/eda.py` → `eda_summary.json`, charts in
`analysis/charts/` (levels_by_season, coverage_by_season,
levels_by_group, halves_constants, trait_reliability). Virgin-season
(2025) levels are inventory only — they were NOT used to choose any
line, arm, or window; line selection uses the dev scored window
2022–2024 only. 2026 is inventory only.

- **F1 Levels by season (per match)**: goals 3.32 / 3.43 / 3.33 /
  3.51 (dev 2021–2024), 3.48 virgin (inventory), 3.62 reserve
  (inventory). Home-win rate 0.45 / 0.46 / 0.49 / 0.44 (dev);
  draw 0.20 / 0.19 / 0.20 / 0.20; OU2.5 over-rate 0.63 / 0.65 /
  0.63 / 0.71 (dev scored window 2022–2024: 0.650). SOT, corners,
  total shots, stats yellows: **null in every season** — the stats
  feed does not exist in this league at any point, so S/C/K/T have
  no target, no reliability, no halves, no line. This is the
  scores-only verdict, measured, not assumed (brief confirmed).
- **F2 Trait reliability (split-half r, dev era, n=55 teams)**:
  goals-for 0.612, goals-against 0.632 — team scoring and conceding
  traits are reliable enough to rate (Dixon-Coles ratings are
  meaningful here). By era the picture is the same: Kakkonen
  2021–2023 GF 0.610 / GA 0.660 (n=54); Ykkönen 2024 GF 0.564 /
  GA 0.680 (n=12, one season only — wide noise, same direction).
  Season-to-season correlations of team means are weak for attack
  (GF r 0.08 / 0.35 / 0.33 across adjacent dev seasons) than
  defence (GA r 0.18 / 0.43 / 0.30): attack carries poorly across
  seasons in this high-churn tier-3 league, defence carries
  better. Note the 2021–2022 pair is near-zero for both (GF 0.08,
  GA 0.18, 26 common teams) — the expanding fit will lag attack
  churn; the dev gate decides. The 2023→2024 pair (10 common
  teams) is GF 0.33 / GA 0.30: traits DO carry across the
  Kakkonen→Ykkönen restructure, at the same weak level as
  within-Kakkonen pairs.
- **F3 Halves shares (dev era, frozen as config constants)**:
  goals **0.4463** (event times, dev era 2021–2024, 4,730 goals,
  1,353 matches with events; awarded matches excluded). By era:
  Kakkonen 0.4445 (4,164 goals) vs Ykkönen 2024 0.4594 (566
  goals) — no halves break across the restructure (difference
  0.015 on 566 goals is inside noise). Presentation only, never
  fitted on virgin data. SOT / corners / total shots / stats
  yellows halves: **null** — no period splits exist in any season.
  Event-yellows 1H share 0.1277 is computed (141 YellowRed events
  only, no plain Yellows anywhere) but is NOT a frozen constant —
  there is no K market.
- **F4 Entrant transitions (dev era)**: 22 transitions, mean GF
  diff −0.182, GA diff +0.235 vs league team mean — entrants score
  ~0.18 fewer and concede ~0.24 more per match than the league
  team mean, with consistent signs. The X2 offset is therefore
  **measurable**: g_log −0.182, c_log +0.223 (c clamped at
  log 1.25). Split by era: Kakkonen 2022–2023 contributes 20 of
  the 22 transitions (−0.198 / +0.286); Ykkönen 2024 contributes
  only 2 (−0.015 / −0.275, opposite GA sign, n=2 — noise, not a
  contradiction). Contrast NO (25 transitions, +0.057 / +0.035,
  mixed signs, X2 dropped) and FI-Veikkausliiga (−0.358 / +0.263):
  FI-Ykkonen sits with FI — a systematic entrant tilt exists in
  the dev era as measured, so the X2 arm is carried (FEATURES.md).
  Caveat: under the brief split, the offset is identified almost
  entirely from Kakkonen churn; whether it applies to Ykkönen
  entrants is untestable on 2 transitions.
- **F5 Cards feed verdict**: the stats feed carries no yellow_cards
  key in any season, and referee coverage is 0% in every season, so
  no X8 referee arm exists. The event feed carries **zero plain
  Yellow events in the entire corpus** (2021–2026: 0 in every
  season) — only YellowRed (28 / 36 / 63 / 15 in dev) and Red
  (53 / 62 / 104 / 24 in dev) events. Event-derived "yellows" are
  therefore YellowRed events only, 0.07–0.16 per match in dev —
  not a cards target by any definition. K-FI is **not-buildable**
  (no target in either source, in any era, + no referee). This is
  a stronger absence than NO, where plain Yellows at least appear
  from 2024.
- **F6 Line selection (dev over-rates, scored window 2022–2024,
  n=1,010)**: goals OU 1.5 → 0.846, **2.5 → 0.650**, 3.5 → 0.436.
  The closest-to-0.5 line is 3.5, but the frozen goals evaluation
  line is **OU 2.5**, the program standard frozen identically in
  the FI/CH/IL/NO goals preregs (gates must stay comparable across
  leagues; the 3.5 observation is recorded here, not acted on).
  Ladders ±1 around the primary are reported by the engine; gates
  sit at OU 2.5. Home-win rate in the scored window: 0.471; draw:
  0.198; goals/match 3.401. Per era: Kakkonen 2022–2023 OU2.5
  0.638 (n=848) vs Ykkönen 2024 OU2.5 0.710 (n=162) — the 2024
  elevation is the split-phase composition effect, see F7.
  Per Kakkonen group 2022–2023: A OU2.5 0.633, B 0.708, C 0.572
  (C's closest line is 2.5; A/B's is 3.5).
- **F7 Era structure / level shift 2023→2024**: Kakkonen
  2021–2023 pooled 3.359 goals/match (n=1,244, 54 teams) vs
  Ykkönen 2024 3.512 (n=162) — a +0.15 headline shift, but it is
  a **phase-composition effect, not a level break**: Ykkönen 2024
  regular phase is 3.326 (n=132), virtually identical to Kakkonen
  2023 (3.329, n=410), while the 2024 championship (4.133, n=15)
  and relegation (4.533, n=15) split phases pool at 4.333 (n=30)
  and drag the season mean up. Home-win 0.490 → 0.444 and draw
  0.202 → 0.204 are flat; the OU2.5 jump 0.627 → 0.710 is the same
  composition effect. A Dixon-Coles fit on dev ≤ 2024 therefore
  trains on two formats: 1,244 three-group matches + 132 single-
  table matches + 30 high-scoring split-phase matches.
- **F8 Kakkonen group levels + cross-group identification**: the
  three Lohko groups are NOT the same level. Regular-group
  goals/match 2021–2023: A 3.444, B 3.490, **C 3.152** (OU2.5
  0.629 / 0.688 / 0.588); 2022–2023 only: A 3.470, B 3.639,
  **C 3.034** (OU2.5 0.633 / 0.708 / 0.572) — group C runs
  ~0.35–0.60 goals/match below B. Worse, the groups are barely
  identified against each other: 2021 has 0 promotion/playoff
  matches (0 cross-group); 2022 promotion groups are intra-group
  (18 matches, 0 cross-group); **only 2023 links the groups —
  10/10 promo-playoff matches cross-group + 12/14 playoff matches
  cross-group = 22 cross-group matches in the whole dev era**.
  A pooled Dixon-Coles rating therefore anchors the three groups
  together on 22 matches (plus the 2024 single table, where 10 of
  12 teams carry Kakkonen history). Group-level strength
  differences are otherwise absorbed into team ratings that never
  played each other — the dev gate is the judge, but the
  identification weakness is real and must not be hidden.
- **F9 Team continuity across the break**: 11/12 Ykkönen 2024 teams
  played Kakkonen 2021–2023 (10/12 in 2023, 11/12 in 2022, 8/12
  in 2021); 1 team is new to the corpus in 2024. Adjacent-season
  common teams: 2021–2022: 26/36–37; 2022–2023: 27/36–37;
  2023–2024: 10/36→12; 2024–2025: 9/12 (inventory). Churn inside
  Kakkonen is high (~10 entrants/season); the restructure itself
  is not a team break — it is a format break with the same clubs.
- **F10 Format facts**: 36–37 teams/season in Kakkonen (12–13 per
  group), 12 teams/season in Ykkönen. Calendar seasons. Phases per
  season in `inventory_summary.json`. 7 awarded matches, all kept
  as ordinary flagged rows. 55 no-event matches, all scoreless.

## Window consequence

Goals has a full dev under the brief split: warm-up 2021 + scored
2022–2024 (n=1,010), season-blocked expanding fit — but 848 of
those 1,010 scored matches are Kakkonen three-group matches and
only 162 are Ykkönen. S/C/K/T have no dev window at all — not a
thin dev, a nonexistent one. The split was not moved to manufacture
a window for them; the split question (MODEL_DESIGN.md) is whether
the Kakkonen seasons belong in dev at all.
