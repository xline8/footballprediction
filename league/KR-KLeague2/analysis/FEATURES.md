# Phase 5 — Features: KR-KLeague2

J1 template X1–X9, judged in THIS league's data (EDA numbers).
All adopted features use strict pre-season cutoffs (season-blocked:
features for a target season are computed only from matches before
that season starts).

- X1 xG blend — DROPPED. Data absent: `expected_goals` appears in
  0 of 1,407 matches and the shotmap is empty in every season. The
  goals Gate Zero degenerates to goals-only Dixon-Coles.
- X2 mover offset — ADOPTED as a goals arm. The parent tier
  KR-KLeague1 is built; its corpus exists and every relegated mover
  is found by team ID in the prior K1 season (2022 Gwangju FC; 2023
  Gimcheon Sangmu, Seongnam FC; 2024 Suwon Samsung Bluewings; virgin
  2025 Incheon United). Construction frozen in PREREG_G_KR2 (shrunk
  prior-season K1 scoring/conceding rates → log-rating offsets for
  teams with no prior K2 history). Promoted-from-K3 teams (Gimpo,
  Cheonan, Cheongju, Hwaseong) have no corpus and get no offset.
- X3 set-play xG share — DROPPED. Data absent (no xG keys at all).
- X4 xG per shot — DROPPED. Data absent (no shotmap, no xG).
- X5 trailing target rates — ADOPTED. The count Gate Zero itself:
  team for/against traits are reliable (SOT 0.64/0.73, corners
  0.72/0.49, shots 0.76/0.63, stats yellows 0.75/0.66).
- X6 xGOT per shot — DROPPED. Data absent (no shotmap).
- X7 box-touch multiplier — ADOPTED as an arm for corners, SOT and
  total shots. Reliability for/against 0.804/0.683. Coverage is the
  constraint: 25.5% (2022), 38.0% (2023), 97.9% (2024), 100% (2025),
  so the arm carries the frozen min-8 trailing-match guard and the
  both-teams-active rule; in early dev it is mostly inactive, which
  the results must show, not hide.
- X8 referee strictness — DROPPED. Referee identity is present in
  only 400 of 1,397 regular matches (10–52% by season) and only
  3 referees reach ≥20 matches corpus-wide (2 in the stats era);
  split-half strictness reliability is inestimable (0 valid splits).
  Cards ships Gate Zero only.
- X9 possession / big-chance covariates — DROPPED (not used).
  Reliability is real (possession 0.867, big chance 0.743/0.607) but
  this build's single-variant discipline prefers X7 for the count
  markets (box touches have the direct territorial mechanism into
  corners/shots), and no frozen covariate construction is ported.
  Recorded as available for a future prereg, not silently included.
- SOT ratio construction (production v5 pattern) — DROPPED as an arm:
  the on-target ratio is not a reliable team trait in this league
  (split-half r = 0.006). SOT Gate Zero rates the target directly.

Frozen halves constants (splits era 2023–2025, presentation only;
2H share = 1 − 1H share): goals 0.396 (HT from Goal events,
n=672), SOT 0.415 (n=709), corners 0.425 (n=710), total shots 0.421
(n=710), cards 0.330 (stats period splits, n=675). Every constant was
measured from THIS league's CSV; no constant is imported from any
other league. Lineups, absence, standings, h2h, attendance, momentum
and red cards are rejected (leakage / no evidence / rare events), as
in the template.
