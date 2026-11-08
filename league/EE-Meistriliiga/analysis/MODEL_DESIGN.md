# Model design — EE-Meistriliiga

The only buildable candidate is **G-EE (goals)**. S-EE (SOT), C-EE (corners),
T-EE (total shots) and K-EE (cards) are not buildable: stats and shotmap
targets are absent everywhere, and the card feed has no valid multi-season
scored dev window.

G-EE uses production Dixon–Coles unmodified: Gate Zero, `model_v2.py` class
`DC`, half-life 270 days, production rho grid, MAXG=10 and production tau
correction. Primary line is OU2.5.

Arms (maximum three): Gate Zero; SHRINK, only if the G-J2 post-mortem applies,
pulling a short-history team rating toward zero by the frozen factor `n/(n+k)`
(k and threshold must be fixed before fitting); and X2 mover offset. X2 is
adopted from the entrant EDA with EXPANDING offsets estimated only from
entrants in seasons strictly before the target season S: for an entrant into
S, add attack `log(max(mu+dGF_S,0.10)/mu)` and defence
`log((mu+dGA_S)/mu)` to the fitted ratings, where mu is the decay-weighted
league mean and (dGF_S, dGA_S) are frozen per S — 2023: (−0.358333,
+1.030556); 2024: (−0.440278, +0.726389); 2025: (−0.588889, +0.716667);
2026 (virgin): (−0.498611, +0.626389). X2 is inactive for target 2022 (no
prior entrant exists). The all-entrant pooled figure (dGF −0.381, dGA
+0.641) is descriptive only and is NOT used, because it includes the 2026
virgin-season entrant's own outcomes. The exact entrant rule is frozen in
the preregistration.

Dev is expanding, season-blocked walk-forward: warm-up 2021; scored seasons
2022–2025; each fit uses only matches strictly before the target season’s first
match. Virgin is complete 2026 (180 matches, ending 2026-11-07); no confirmatory
window. No fitting, engine or dev harness is part of Phase A.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's, (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp for home-win rate and OU2.5 over-rate, breach within 1 SE is PROVISIONAL PASS else FAIL, (iii) per-season sign check for variants. Both-pass rule: lower pooled virgin 1X2 LL ships; if none passes, G-EE FAIL and nothing ships.
