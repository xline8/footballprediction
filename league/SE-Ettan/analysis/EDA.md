# Step 3/4 — EDA & Visualization: SE-Ettan

Evidence from `analysis/eda.py` → `eda_summary.json`, charts in
`analysis/charts/` (levels_by_season, coverage_by_season,
halves_constants, trait_reliability). Season 2026 is not in any
number here. Virgin-season (2025) levels appear in the inventory
table only — they were NOT used to choose any line, arm, or window.
Line selection, halves constants, trait reliability, and entrant
transitions use dev-era (≤ 2024) data only.

- **F1 Levels by season (per match)**: goals 3.290 / 3.025 / 2.875 /
  3.063 in 2021–2024 (dev scored window 2022–2024 mean 2.988; the
  partial 2021 season is the highest at 3.290, on only 262 matches
  with a different fixture mix — it is a warm-up, not a level to
  chase). Norra outscores Södra in **every** season: 3.366 / 3.208 /
  2.958 / 3.321 (Norra) vs 3.197 / 2.842 / 2.792 / 2.804 (Södra) in
  2021–2024 — a persistent ~0.3–0.5 goals/match group gap, visible
  in `levels_by_season.png`. It is recorded as a format fact; the
  goals engine rates teams, not groups, and no group term is proposed
  (a group term would be a design decision for Phase 3, not an EDA
  finding). Home goals 1.6104 vs away 1.3771 in the scored window.
  Virgin 2025 (inventory only): 3.198 overall (Norra 3.363, Södra
  3.033). Stats-era levels do not exist in any season: SOT, corners,
  total shots, stats yellows are null everywhere.
- **F2 Trait reliability (split-half r, dev era)**: goals-for **0.562**
  (n=57 teams, dev 2021–2024) and goals-against **0.742** — the goals
  trait is reliable enough to rate. On the scored window only
  (2022–2024, n=49): goals-for **0.703**, goals-against **0.604**.
  The 2021–2024 figure is the conservative one (the partial 2021
  season gives some teams as few as ~8–16 matches, which depresses
  the split-half correlation); both pass. Season-to-season
  goals-for correlation (overlapping teams): 0.306 (2021→2022, n=22),
  0.588 (2022→2023, n=24), 0.393 (2023→2024, n=23) — positive in all
  three transitions, consistent with a real team trait plus heavy
  year-to-year churn (8–10 entrants per season). SOT, corners,
  shots, stats yellows, possession: **not measurable on dev** — the
  targets are absent in every season, so no split-half correlation
  exists to compute. The count candidates are not-buildable on trait
  grounds as well as on window grounds. Event-derived yellows are
  the one exception — see F5.
- **F3 Halves shares (dev era, frozen as config constants)**: goals
  **0.4385** (event times, 1,885 goals, 1,439 matches, 2022–2024;
  per-season shares 0.4435 / 0.4464 / 0.4260, stable). 2021 has no
  events, so it contributes nothing; the awarded match 4398485 is
  excluded (corrupt event feed). SOT / corners / total shots /
  yellows 1H shares from splits are **NOT computable**: 0 matches
  with FirstHalf/SecondHalf splits in any season. No halves constant
  exists for any count market, and none is invented — the config
  freezes only `goals_1h_share`. Event-time 1H yellows are
  **0.2841** (1,375 of 4,840 event yellows, 2022–2024; per-season
  0.3000 / 0.2781 / 0.2737) — reported as descriptive evidence for K
  only, not frozen as a constant for any built market, because K is
  not-buildable (F5).
- **F4 Entrant transitions (dev era)**: 27 transitions (10 in 2022,
  8 in 2023, 9 in 2024; 2021 is the corpus baseline, not a
  transition), mean GF diff **−0.013**, GA diff **+0.081** vs league
  team mean. GF is negative in 13 of 27, GA positive in 15 of 27 —
  no systematic tilt in either direction. Per-season means:
  2022 +0.064 / −0.082, 2023 +0.013 / +0.067, 2024 −0.120 / +0.276;
  the signs flip between seasons. The X2 entrant offset is therefore
  **NOT adopted for G-SE** (FEATURES.md / MODEL_DESIGN.md). Why SE
  differs from QA (−0.356 / +0.360, adopted there): SE entrants mix
  relegated Superettan sides (strong — e.g. GAIS, Falkenbergs FF and
  Vasalunds IF all posted positive GF diffs in 2022) with promoted
  Division 2 sides (weak — e.g. Team TG FF −0.879 / +1.021 in 2022),
  and the two cancel. With 27 transitions the null is well measured,
  not a small-sample artefact. No team switched groups between
  seasons, so entrant status is not confounded with a group move.
- **F5 Cards feed verdict — the one judgement call in this EDA.**
  The event feed DOES carry plain Yellow events in dev (4,745 plain
  Yellows, 98 YellowRed, 113 Red in 2021–2024; event yellows
  3.4375 / 3.2813 / 3.3708 per match in 2022–2024), and the
  event-yellows team trait is measurable and moderately reliable
  (split-half r **0.549**, n=49 teams, 2022–2024). That is materially
  better evidence than QA had (zero plain Yellows in dev). **K-SE is
  still not-buildable under the frozen split, for three independent
  reasons, any one of which suffices**: (a) there is no stats feed
  anywhere, so the canonical cards target (stats yellows) does not
  exist and the event-derived series cannot be validated against any
  official count — in QA the event feed was shown to undercount
  structurally when the two feeds coexisted, and SE has no
  coexistence window to check; (b) the dev era has no complete window
  from one consistent source — 2021 (the warm-up season) has zero
  events, so an event-yellows model would have no target at all in
  its first dev season; (c) X8 is impossible — referee coverage is 0%
  in every season, so no referee arm exists. This is recorded here so
  Jarvis can see the evidence and decide: **revisiting K would need a
  program-level decision to (i) adopt event-derived yellows as the
  target by definition and (ii) re-split dev to start in 2022.** That
  decision is NOT made here, and no K engine is built in this league
  without it. The 1H yellows share (0.2841) and the trait r (0.549)
  are preserved in `eda_summary.json` for that decision.
- **F6 Line selection (dev, scored window 2022–2024, n=1,440)**:
  goals OU over-rates 1.5: 0.791, 2.5: **0.583**, 3.5: 0.340. The
  over-rate closest to 0.5 is 2.5, which is also the program-standard
  gate line (FI/CH/EC/DK/QA all gate on OU 2.5) — no conflict. Home
  win rate 0.4313, draw rate 0.2097 in the same window. Including the
  partial 2021 season changes almost nothing (OU 2.5: 0.594). By
  group, OU 2.5 over-rates are 0.625 (Norra) vs 0.542 (Södra) — the
  same group scoring gap as F1, recorded, not acted on. SOT /
  corners / total shots / yellows lines are null: no dev window
  exists to select a line on. Goals distribution (scored window):
  0: 59, 1: 242, 2: 299, 3: 350, 4: 233, 5: 136, 6: 66, 7: 42,
  8: 9, 9: 3, 11: 1.
- **Window consequence (the central finding)**: the stats era never
  starts. Stats markets (S/C/K/T) have **zero** warm-up seasons and
  **zero** scored dev seasons — not a thin dev, no dev at all. The
  frozen split (dev ≤ 2024, virgin 2025, 2026 untouched reserve) is
  NOT moved to manufacture one. S/C/K/T verdicts at Phase 6 are
  therefore **not-buildable**, recorded pre-fitting. Only G-SE
  proceeds to Phase 3/4, with warm-up 2021 (partial, 262 matches, no
  events — ratings for teams with no 2021 history start unrated, per
  the engine's standard handling) and scored dev 2022–2024 (n=1,440).
  The 2021 partial season is a second-order caveat for G, not a
  blocker: the goals target itself is complete in every played 2021
  match (scores exist for all 262), only the events-derived fields
  are missing.
