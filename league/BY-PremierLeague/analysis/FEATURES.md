# Step 5 — Feature Engineering: BY-PremierLeague

J1-template features, adopted or dropped with the EDA evidence for
each. Only adopted features may be consumed by MODEL_DESIGN.md.

## Adopted

- **X1 goals blend → goals-only fallback.** No xG exists in any
  season (no stats feed, no shotmap), so the X1 blend's documented
  fallback applies: the Dixon-Coles observation is goals only in
  every match. Evidence: EDA F1 (xg_rows 0/1,394).
- **Goals attack/defence team traits.** Split-half r 0.855 (GF) /
  0.947 (GA) on dev-era team matches, n=20 teams (EDA F2). Strong —
  adopted as the DC ratings, with the usual caution: the ratings
  are re-fitted expanding, never carried frozen across seasons,
  and the dev gate decides.
- **X2 entrant offset — KEPT.** 8 dev entrant transitions, mean GF
  −0.325 / GA +0.426, signs consistent (GF negative 8/8, GA
  positive 7/8; EDA F4). Clamped offsets: g_log −0.223 (= log 0.8),
  c_log +0.223 (= log 1.25) — the raw means hit the program clamp
  on both sides. This is the opposite decision to CH/NO/FR, where
  the tilt was ~0 and mixed, and the same decision as FI, which
  adopted X2 on 8 transitions at GF −0.210 / GA +0.159; BY's tilt
  is larger and equally one-directional. The X2 arm is a genuine
  variant to test against Gate Zero (SHRINK stays the other
  variant arm).
- **Goals 1H share constant 0.4314** (EDA F3). Presentation-only
  halves split for predictions output; never a fitted parameter.

## Dropped (with reason — every one is a data absence, not a modelling choice)

- **X1 xG blend** — no xG in any season.
- **X3 set-play share** — needs expected_goals_set_play; absent.
- **X4 on-target ratio inputs** — needs ShotsOnTarget; absent.
- **X6 shot volume** — needs total_shots; absent.
- **X7 box touches / territory for corners** — needs
  touches_opp_box; absent.
- **X8 referee for cards** — referee named in 0/1,394 matches;
  absent. (Also moot: K is not-buildable, EDA F5.)
- **X9 keeper saves** — needs keeper_saves; absent.
- **SOT / corners / total shots / yellows traits** — no target
  exists in any season (stats feed 0%), so no trait reliability is
  measurable (split-half r null, n=0 teams with a target) and no
  1H share is computable (0 matches with period splits). S/C/K/T
  are not-buildable on feasibility grounds (see their verdict
  files); this is not a gate FAIL.

## Frozen halves constants (dev era only)

| Constant | Value | Source |
|---|---|---|
| goals_1h_share | **0.4314** | event times, dev 2021–2024, 2,348 goals |
| yellow_cards_1h_share | null | no period splits, no K market |
| sot_1h_share | null | no period splits |
| corners_1h_share | null | no period splits |
| total_shots_1h_share | null | no period splits |
