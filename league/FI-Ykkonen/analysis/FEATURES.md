# Step 5 — Feature Engineering: FI-Ykkonen

J1-template features, adopted or dropped with the EDA evidence for
each. Only adopted features may be consumed by MODEL_DESIGN.md.

## Adopted

- **X1 goals blend → goals-only fallback.** No xG exists in any
  season (no stats feed, no shotmap), so the X1 blend's documented
  fallback applies: the Dixon-Coles observation is goals only in
  every match. Evidence: EDA F1 (xg_rows 0/1,730).
- **Goals attack/defence team traits.** Split-half r 0.612 (GF) /
  0.632 (GA) on dev-era team matches, n=55 teams (EDA F2). Adopted
  as the DC ratings. Season-to-season attack correlation is weak
  (0.08–0.35), recorded as a risk, not a drop: the ratings are
  re-fitted expanding, never carried frozen across seasons.
  Reliability holds within each era separately (Kakkonen 0.610 /
  0.660; Ykkönen 2024 0.564 / 0.680), so the trait is not an
  artefact of pooling eras.
- **X2 entrant handling.** 22 dev entrant transitions, mean GF
  diff −0.182 / GA diff +0.235, consistent signs (EDA F4):
  g_log −0.182, c_log +0.223 (clamped at log 1.25). Adopted as the
  X2 arm (SHRINK + entrant offset, per the FI prereg definition:
  offset applies only in the entrant's first season in the
  corpus, identified by absence from the previous season).
  Caveat recorded: the offset is identified almost entirely from
  Kakkonen churn (20/22 transitions); Ykkönen 2024 contributes
  only 2 transitions with an opposite GA sign.
- **Goals 1H share constant 0.4463** (EDA F3). Presentation-only
  halves split for predictions output; never a fitted parameter.
  Stable across eras (Kakkonen 0.4445, Ykkönen 2024 0.4594).

## Dropped (with reason — every one is a data absence, not a modelling choice)

- **X1 xG blend** — no xG in any season.
- **X3 set-play share** — needs expected_goals_set_play; absent.
- **X4 on-target ratio inputs** — needs ShotsOnTarget; absent.
- **X6 shot volume** — needs total_shots; absent.
- **X7 box touches / territory for corners** — needs
  touches_opp_box; absent.
- **X8 referee for cards** — referee named in 0/1,730 matches;
  absent. (Also moot: K is not-buildable, EDA F5.)
- **X9 keeper saves** — needs keeper_saves; absent.
- **SOT / corners / total shots / yellows traits** — no target
  exists in any season (stats feed 0%), so no trait reliability is
  measurable (split-half r null, n=0 teams with a target) and no
  1H share is computable (0 matches with period splits). S/C/K/T
  are not-buildable on feasibility grounds (see their verdict
  files); this is not a gate FAIL. Cards additionally: the event
  feed carries zero plain Yellow events in the whole corpus, so
  there is no event-based yellows target either.

## Frozen halves constants (dev era only)

| Constant | Value | Source |
|---|---|---|
| goals_1h_share | **0.4463** | event times, dev 2021–2024, 4,730 goals |
| yellow_cards_1h_share | null | no period splits, no K market (0 plain Yellow events) |
| sot_1h_share | null | no period splits |
| corners_1h_share | null | no period splits |
| total_shots_1h_share | null | no period splits |
