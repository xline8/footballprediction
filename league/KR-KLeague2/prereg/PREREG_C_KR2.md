# Pre-registration — C-KR2 (K League 2 corners)

Frozen 2026-11-10 before any fitting. Reference pattern: production
corners family (Poisson team attack/defence ratings + Negative
Binomial totals). Population: regular season only; matches with the
corners target present. Dev: seed 2022 (219 with target), scored
2023–2024 (461). Virgin: complete 2025 (273, target-complete), read
ONCE and only for dev-passing arms. 2026 reserved, unread. Primary
line OU 8.5; scored-dev over-rate 0.521. Secondary lines 9.5 / 10.5
reported.

Arms:
- Gate Zero: season-blocked Poisson ratings on corners (IPF,
  half-life 270 days at the season-start cutoff, prior 0.25),
  expected total λh + λa, NB over-probabilities with r = the frozen
  moment estimate on the training window (r = Σμ² / Σ((y−μ)²−μ),
  capped [2, 500]).
- X7 box-touch multiplier: Gate Zero with each side's λ multiplied
  by sqrt(att_index × opp_def_index) clipped to [0.5, 2.0], indices
  from box-touch for/against per match over pre-season matches with
  touches data; active only when BOTH teams have ≥8 such matches,
  else the multiplier is 1 for that match. (Box touches are the
  strongest auxiliary trait in this league, r 0.804/0.683; the X9
  possession/big-chance covariates are recorded DROPPED in
  FEATURES.md and are not used.)

Baselines: league base rate (prior-seasons over-rate at the line)
and naive trailing-10 (team last-10 for/against means before the
season, combined (own_for + opp_against)/2 per side).

Dev gate: an arm passes dev iff its pooled LL at 8.5 beats BOTH
baselines' pooled LL at 8.5. Variants additionally need the
per-season sign check (variant LL ≤ Gate Zero LL in at least 1 of
the 2 scored dev seasons — at least half). If Gate Zero fails dev,
the candidate FAILS and the virgin is NOT read for any arm.

Virgin gate (per arm): LL at 8.5 ≤ Gate Zero virgin LL AND ≤ the
better virgin baseline LL; calibration |mean predicted over-rate −
actual over-rate| ≤ 1 pp clean PASS, ≤ 1 pp + 1 SE PROVISIONAL PASS,
else FAIL. Both-pass selection: lowest virgin LL; ties prefer Gate
Zero, then X7. On PASS the winning arm's fitted params and virgin
per-match predictions ship, with halves presentation via this
league's frozen corners 1H share 0.425.
