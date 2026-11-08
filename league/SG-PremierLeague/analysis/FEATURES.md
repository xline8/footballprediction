# Step 5 — Feature Engineering: SG-PremierLeague

J1-template features, adopted or dropped with the EDA evidence
for each. Only adopted features may be consumed by
MODEL_DESIGN.md.

## Adopted

- **X1 goals blend → goals-only fallback.** No xG exists in any
  season (no stats feed, no shotmap), so the X1 blend's
  documented fallback applies: the Dixon-Coles observation is
  goals only in every match. Evidence: EDA F1 (xg_rows 0/555).
- **Goals attack/defence team traits.** Split-half r 0.881 (GF)
  / 0.869 (GA) on dev-era team matches, n=9 teams (EDA F2).
  Strong — adopted as the DC ratings, with the usual caution:
  the ratings are re-fitted expanding, never carried frozen
  across seasons, and the dev gate decides.
- **Goals 1H share constant 0.4404** (EDA F3). Presentation-only
  halves split for predictions output; never a fitted parameter.

## Dropped (with reason)

- **X1 xG blend** — no xG in any season.
- **X2 entrant offset — DROPPED on evidence.** Exactly 1 dev
  entrant transition (Brunei DPMM returning 2023, GF −0.468 /
  GA −0.301; EDA F4): below the ≥3-transition minimum the
  program rule requires before any offset is non-zero, and the
  GA sign contradicts the entrant pattern (DPMM is a strong
  guest club, not a promoted side). Same decision as CH/NO/SE;
  opposite of BY/FI (8 consistent transitions). G-SG runs Gate
  Zero + SHRINK only.
- **X3 set-play share** — needs expected_goals_set_play; absent.
- **X4 on-target ratio inputs** — needs ShotsOnTarget; absent.
- **X6 shot volume** — needs total_shots; absent.
- **X7 box touches / territory for corners** — needs
  touches_opp_box; absent.
- **X8 referee for cards** — referee named in 0/448 dev matches;
  absent. (Also moot: K is not-buildable, EDA F5.)
- **X9 keeper saves** — needs keeper_saves; absent.
- **SOT / corners / total shots / yellows traits** — no target
  exists in any season (stats feed 0%), so no trait reliability
  is measurable (split-half r null, n=0 teams with a target) and
  no 1H share is computable (0 matches with period splits).
  S/C/K/T are not-buildable on feasibility grounds (see their
  verdict files); this is not a gate FAIL.

## Frozen halves constants (dev era only)

| Constant | Value | Source |
|---|---|---|
| goals_1h_share | **0.4404** | event times, dev 2021–2024/2025, 1,905 goals |
| yellow_cards_1h_share | null | no period splits, no K market |
| sot_1h_share | null | no period splits |
| corners_1h_share | null | no period splits |
| total_shots_1h_share | null | no period splits |
