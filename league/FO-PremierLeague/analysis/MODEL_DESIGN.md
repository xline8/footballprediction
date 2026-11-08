# Phase 4 — Model Design: Faroe Islands Premier League

Phase A freezes two buildable candidates and three not-buildable
preregistration notes. Season 2021 is the seed. Development is the
season-blocked 2022–2025 window (539 eligible matches); 2026 is the complete
virgin season (135 matches) and is not read for fitting.

## G-FO goals

Gate Zero is the production Dixon-Coles reference (`model_v2.py`):
goals-only, HL 270, rho grid, 14 sweeps, damping 0.7, +0.25 smoothing, and
MAXG 10. The only variant is SHRINK: fitted attack and defence ratings are
multiplied by 0.85 toward the league mean; home advantage is untouched. This
is pre-registered for the two-club seasonal churn and stale returnee history
observed in the league. No X2/X3 arm exists because those features are
dropped.

Primary line: OU2.5, with development over-rate **0.659**. Development gates
are pooled 1X2 log loss, RPS, and OU2.5 log loss against climatology; the
candidate must beat both baselines. Virgin legs are log loss no worse than
Gate Zero and no worse than the best baseline, calibration
`|mean prediction - actual| <= 1.0pp` pooled (within one standard error is a
provisional pass), plus per-season sign checks for variant arms. Both-pass
rule applies.

## K-FO cards

Gate Zero follows production `model_cards.py`: decayed venue-split team
yellow ratings, K_PRIOR 8, negative-binomial target, and dispersion `r` by
the production method-of-moments procedure. SHRINK changes only K_PRIOR to
16. No referee arm exists. The chronological online pass uses 2021 as warmup
and evaluates 2022–2025 development, then 2026 virgin.

Primary line is 3.5 (development over-rate **0.594**); 4.5 is secondary.
Development is LL@3.5 against the league base rate and naive trailing-10,
and must beat both. Virgin gates use the same LL, baseline, calibration, and
per-season sign-check rules as G-FO.

## Not-buildable preregistration notes

S-FO, C-FO, and T-FO are not buildable in this corpus. SOT, corners, and
total shots are absent from all 810 payloads: usable stats 0/810 and shotmap
shots 0/810. Their preregistration files are owned by the coordinator; this
document records the design decision and the data gate only. No substitute
event proxy is silently promoted to one of these targets.

## Halves presentation

Both buildable markets present FT plus 1H/2H using frozen shares goals=0.441
and unified yellows=0.348. This is presentation only; no half model or
per-team half feature is fitted.
