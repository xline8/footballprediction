# Step 5 — Features: PY-DivisionProfesional (J1 template X1–X9, judged in THIS league)

Global causality contract as in J1 FEATURES §1 (strictly pre-match
inputs, trailing/expanding-with-decay windows, ratio-of-sums, NaN ⇒
arm inactive, never filled from the future). Era note that governs
everything below: **count features exist only from 2025 - Apertura**;
goals features exist for all 1,480 matches.

| # | Feature (J1 analogue) | Verdict | Reason (this league's number) |
|---|---|---|---|
| X1 | Blend observation pair (goals, xG) | **ADOPTED, degraded goals-only** | xG does not exist (shotmap 0% in all 1,480 files). Production blend's documented goals-only fallback applies to 100% of observations — exactly the BG-SecondLeague situation. |
| X2 | Mover tier offset | **DROPPED** | Split-tournament calendar: entry happens once a year (Apertura) with ≤ 2 movers/year from División Intermedia, an unmodelled league; sample too thin to estimate an offset inside dev, and the sanctioned SHRINK arm covers the measured failure mode (new-team extreme lambdas). |
| X3 | Set-play xG share/rate | **DROPPED** | Data absent: no xG of any kind (shotmap 0%). |
| X4 | xG per shot | **DROPPED** | Data absent: no shotmap. |
| X5 | Trailing target-rate means (naive/ensemble inputs) | **ADOPTED** (stats era only) | Target traits are reliable here (F2: SOT-for 0.83, corners-for 0.56, shots-for 0.81, yellows-against 0.51). Available only where the feed lives (2025+); the min-presence rule handles the one feed-missing clásico. |
| X6 | Attacking xGOT per shot | **DROPPED** | Data absent: no shotmap, no xGOT. |
| X7 | Opp-box touches for/against (corners multiplier) | **ADOPTED** | Touches trait r = 0.70 (F2); per-match corr with corners 0.389. Present in 100% of stats-era matches. Consumed by C-PY's X7 arm. |
| X8 | Referee yellow rate | **DROPPED** | Dev-era appointment coverage 11.1% (1.5% in 2026 - Apertura): the arm would be inactive for ~89% of dev rows and unvalidatable; its apparent strictness signal (r = 0.686) rests on 7 referees and is concentrated in the virgin era, which may not rescue an arm. K-J2 precedent. Cards = Gate Zero only. |
| X9 | Production corners covariates (possession, big chances) | **ADOPTED** | Both keys present in 100% of stats-era matches; big-chance trait r = 0.96 (F2). Carried unchanged inside corners Gate Zero, as in production. |
| SHRINK | New-team rating shrinkage (goals variant arm) | **ADOPTED** | Sanctioned G-J2-lesson arm, pre-registered in PREREG_G_PY: promoted clubs enter each Apertura with 0 in-league matches in the decay window and Gate Zero's unseen=mean rule plus early results can produce extreme lambdas in openers. |

Rejected outright (J1 §3 analogues): per-team/per-match half shares
(R1 — F3 true variance ≈ 0), finishing/conversion covariates (R2/R3 —
no xG to define them, and noise in J1), standalone on-target rate as a
covariate (R4 — the trait is real here, r = 0.48, but it is exactly
v5's internal Beta-Binomial ratio component; a standalone covariate is
the rejected object, as in J1), lineup/absence (R6, closed program-wide),
standings/h2h snapshots (R9, post-match leakage), reds as target (R12).

## Frozen halves constants (presentation only, from F3)

goals **0.418** · SOT **0.442** · corners **0.492** · total shots
**0.465** · cards **0.327** (event-based). FT + 1H/2H splits on PASS
only; halves never enter any gate.
