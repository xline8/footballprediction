# Step 3 — EDA: UY-LigaAUF

All numbers trace to `analysis/eda_summary.json`
(`inventory_summary.json` holds the per-season inventory). EDA script:
`analysis/eda.py`; charts: `analysis/make_charts.py` →
`analysis/charts/`. Every fitting-relevant number below is computed
on the dev era only (season_start ≤ 2024) unless labelled inventory.
Virgin 2025 levels are shown for inventory only and are NOT used to
choose lines, arms, or windows; 2026 is inventory only.

## F1 — Feed era structure (the deciding finding)

Stats feed 0% in every season (0/1,717 matches, 0 stats keys in any
raw JSON); shotmap 0% (0/1,717); referee named 0% (0/1,717); period
splits 0% (0/1,717). Events 97.8% (1,679/1,717); lineups 0% in
2021–2022, 92.7% in 2023, 100% in 2024–2026. Coverage chart:
`charts/coverage_by_season.png`.

## F2 — Trait reliability (dev era, split-half odd/even chronological)

- `goals_for` r = 0.588 (n=24 teams); `goals_against` r = 0.809
  (n=24). Team attack/defence persist — the Dixon-Coles ratings
  have signal to fit.
- Season-to-season (13 overlapping teams per pair): goals_for r
  0.273 (2021–22), 0.551 (2022–23), 0.680 (2023–24); goals_against
  r 0.324, 0.554, 0.423. Reliability rises as the corpus deepens;
  the 2021–22 pair is the noisiest (2021 is short: 241 matches,
  no Intermedio).
- SOT / corners / total shots / yellows / possession: split-half r
  null, n=0 teams — targets absent in dev, reliability not
  measurable. Chart: `charts/trait_reliability.png`.

## F3 — Halves shares (dev era, frozen constants)

- Goals 1H share (event times, dev, excluding the 2 mismatched
  matches): **0.4276** (2,664 goals, 1,096 matches). Per-season:
  2021: 0.4279 (610 goals), 2022: 0.4138 (650), 2023: 0.4300 (686),
  2024: 0.4373 (718) — stable across seasons; the pooled 0.4276 is
  the frozen goals halves constant.
- SOT / corners / total shots / yellows 1H shares: NOT computable
  (0 matches with FirstHalf/SecondHalf splits in any season). No
  constant exists for any count market. Chart:
  `charts/halves_constants.png`.

## F4 — Entrant transitions (dev era, X2)

9 entrant transitions in dev (a team absent in the immediately
preceding season; 2021 yields none as first corpus season):
2022 Danubio (GF −0.069, GA −0.339), Defensor Sporting (+0.039,
−0.123), Albion (−0.177, +0.445); 2023 La Luz (−0.008, +0.559),
Racing (−0.035, −0.008), Cerro (−0.305, −0.197); 2024 Miramar
Misiones (−0.244, +0.215), Rampla Juniors (−0.271, +0.350),
Progreso (−0.082, +0.404). Mean GF diff −0.128 (negative in 8/9),
mean GA diff +0.145 (positive in 5/9). Dev scored mean team goals
1.1520 (895 matches). Frozen entrant log offsets (prereg):
attack log((1.1520−0.1280)/1.1520) = −0.1178; defence
log((1.1520+0.1452)/1.1520) = +0.1188, applied as −0.1188 to the
defence exponent. Note the GA signal is weaker than the QA
analogue (5/9 positive vs QA 4/4) and rests on 9 transitions —
recorded here, not adjusted for.

## F5 — Levels and line selection (dev scored window 2022–2024, n=895)

Goals/match by season: 2021: 2.531, 2022: 2.191, 2023: 2.287,
2024: 2.434 (virgin 2025: 2.333, reserve 2026: 2.377 — inventory
only). OU over-rates on the dev scored window: 1.5: 0.6715,
2.5: 0.4045, 3.5: 0.2045 → primary line OU **2.5** (closest to 0.5).
Home-win 0.381 / draw 0.282 / away-win 0.337 on the same window.
Chart: `charts/levels_by_season.png`.

## F6 — Why S/C/K/T are not-buildable (frozen, pre-fitting)

- **S (SOT), C (corners), T (total shots):** the target exists in NO
  season under any source — the stats feed is 0% in 2021–2026, so
  there is no dev season, no warm-up season, no halves constant,
  and no measurable trait reliability for any of them. This is the
  FI total-shots case in its strongest form: not a definition break
  within a dev window, but the complete absence of a dev window.
- **K (cards/yellows):** no consistent yellows target in dev under
  either source. Stats-feed yellows: absent in every season (0%).
  Event-feed fallback: plain Yellow Card events exist ONLY from
  2023 (2021: 0, 2022: 0; 2023+: 1,543–1,659/season) — a
  target-definition break inside dev, exactly the NO-2Divisjon
  precedent (there: Yellows only from 2024). A yellows target
  defined on events would have no window in 2021–2022 (warm-up +
  first scored season) and a two-season window in 2023–2024.
  Referee data is absent in dev (named in 0/1,717 matches, every
  season), so no X8 referee arm exists. No 1H yellows constant is
  computable on dev as a frozen constant.
- The frozen split is not moved to manufacture a dev window for
  any of them. S/C/K/T may be pre-registered fresh once a dev
  target exists; they may not be rescued inside this prereg.

## F7 — Format facts

16 teams/season; Apertura 120 + Clausura 120 + Intermedio 57 +
Final Stage 1–3 per complete season; 2021 has no Intermedio (241
matches). 1 awarded match (3834312, 2022, 0–3). 38 event-less
matches, all 0–0 (2021: 15, 2022: 20, 2023: 3) — a feed gap for
scoreless draws, no modelling impact (scoreStr is the score).
26 team ids in the corpus.
