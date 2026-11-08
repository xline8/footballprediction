# Step 5 — Feature Engineering: IN-IndianFootballLeague

J1-template features, adopted or dropped with the EDA evidence for
each. Only adopted features may be consumed by MODEL_DESIGN.md.

## Adopted

- **X1 goals blend → goals-only fallback.** No xG exists in any
  season (no stats feed, no shotmap), so the X1 blend's documented
  fallback applies: the Dixon-Coles observation is goals only in
  every match. Evidence: EDA F1 (xg_rows 0/608).
- **Goals attack/defence team traits.** Split-half r 0.608 (GF) /
  0.462 (GA) on dev-era team matches, n=19 teams (EDA F2).
  Moderate — adopted as the DC ratings, with the usual caution:
  the ratings are re-fitted expanding, never carried frozen across
  seasons, and the dev gate decides.
- **Goals 1H share constant 0.4387** (EDA F3). Presentation-only
  halves split for predictions output; never a fitted parameter.

## Dropped (with reason)

- **X1 xG blend** — no xG in any season.
- **X2 entrant offset — DROPPED.** 6 dev entrant transitions, mean
  GF −0.110 / GA +0.025, signs mixed (GF negative 3/6, GA positive
  3/6; EDA F4). The tilt is ~0 on the conceding side and
  inconsistent on the scoring side — the CH/NO/FR/SE drop pattern,
  not the FI/BY adopt pattern (8 transitions, consistent signs).
  G-IN runs Gate Zero + SHRINK only.
- **X3 set-play share** — needs expected_goals_set_play; absent.
- **X4 on-target ratio inputs** — needs ShotsOnTarget; absent.
- **X6 shot volume** — needs total_shots; absent.
- **X7 box touches / territory for corners** — needs
  touches_opp_box; absent.
- **X8 referee for cards** — referee coverage IS real in dev
  (453/496, 91.3%) but collapses in the virgin (4/66, 6.1%), and
  the feature is moot: K is not-buildable because no yellows
  target exists in dev (EDA F5).
- **X9 keeper saves** — needs keeper_saves; absent.
- **SOT / corners / total shots / yellows traits** — no target
  exists in any dev season (stats feed 0%), so no trait
  reliability is measurable (split-half r null, n=0 teams with a
  target) and no 1H share is computable (0 matches with period
  splits). S/C/K/T are not-buildable on feasibility grounds (see
  their verdict files); this is not a gate FAIL.

## Frozen halves constants (dev era only)

| Constant | Value | Source |
|---|---|---|
| goals_1h_share | **0.4387** | event times, dev 2021/2022–2024/2025, 1,575 goals |
| yellow_cards_1h_share | null | no period splits, no K market |
| sot_1h_share | null | no period splits |
| corners_1h_share | null | no period splits |
| total_shots_1h_share | null | no period splits |
