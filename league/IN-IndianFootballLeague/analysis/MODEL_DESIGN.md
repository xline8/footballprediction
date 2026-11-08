# Step 6 — Model Design: IN-IndianFootballLeague

Feasibility matrix: **goals — target exists in every season**
(608/608 FT scores). **SOT / corners / total shots / yellows —
no target exists in any dev season** (stats feed 0/608, shotmap
0/608, period splits 0/608; plain Yellow events 0 in every dev
season and in the virgin). **Only G-IN is buildable.** S/C/K/T
are not-buildable on feasibility grounds (see their prereg files
and verdict files); the split was not moved to manufacture a
window for them. Cards additionally: referee coverage is real in
dev (91.3%) but collapses in the virgin (4/66), so no X8 arm
could ship even if a target existed.

Windows frozen for the built candidate: virgin = **2025/2026**
(complete, 66 matches — read ONCE, only for dev-passing arms).
2026/2027 (in progress, 10) is untouched as confirmatory reserve.
All rows are ordinary rows (phase flag main / championship /
relegation carried, never filtered), per the frozen phase rule in
DATA_UNDERSTANDING.md. The 4 awarded matches are kept as ordinary
rows with awarded=true; the header score is used, never the
event-derived score.

Implementation divergence from the FI production references,
recorded pre-fitting: the production engine is not runnable from
the bundle, so the G-IN engine is a port of the FI reference
`dc.py` / `arms.py` carried over **verbatim** (iterative sweep
optimiser, 14 sweeps, damping 0.7, +0.25 smoothing, home init
0.28, MAXG = 10, rho grid (0.0, −0.05, −0.10, −0.15) by goals
log-likelihood, decay HL = 270 days), with the harness adapted
from the FI `harness.py` plus the naive trailing-10 baseline as
defined in the IL goals prereg (per-team trailing-10 goals-for
means, independent Poissons, no home advantage). The X1 blend's
documented fallback applies throughout: the observation is
goals-only in every match (no xG exists in this feed), exactly as
frozen in the FI prereg. Constants not carried over are listed in
the prereg.

| Candidate | Gate Zero pattern | Variant arms | Warm-up | Dev scored | Primary line |
|---|---|---|---|---|---|
| G-IN goals | Dixon-Coles Poisson, goals-only (X1 fallback): attack/defence ratings + home advantage, sweep fit, rho grid, score matrix to 10 goals | SHRINK (n<6 prior in-league matches ⇒ attack/defence exponents scaled by n/6 at prediction) | 2021/2022 | 2022/2023–2024/2025 (n=418), season-blocked expanding fit | 1X2 LL/RPS + OU 2.5 |
| S-IN SOT | — not-buildable | — | — | — | — |
| C-IN corners | — not-buildable | — | — | — | — |
| K-IN cards | — not-buildable | — | — | — | — |
| T-IN total shots | — not-buildable | — | — | — | — |

X2 entrant offset is DROPPED pre-fitting (EDA F4: 6 dev
transitions, mean GF −0.110 / GA +0.025, signs mixed — the
CH/NO/FR/SE pattern, not FI/BY). SHRINK is retained as the only
variant arm; note it is expected to be numerically inert under
season-blocked prediction (any team present in a prior season has
≥22 prior matches, so n<6 never binds for a team with a fitted
rating; teams with no fitted rating sit at league mean with
exponents 0.0, which scaling leaves at 0.0) — same observation
as CH/NO/FR/BY. It is run and reported anyway; the gate decides.

Gate legs (identical program-wide, frozen verbatim in the
prereg): dev gate — pooled dev 1X2 LL, RPS and OU2.5 LL of an arm
must beat BOTH baselines (climatology; naive trailing-10), else
the arm is dead and the virgin is NOT read for it; if Gate Zero
fails dev, variants are moot, verdict FAIL. Virgin legs — (i) LL
≤ Gate Zero's and ≤ each baseline's (1X2 and OU2.5); (ii)
calibration |mean predicted − actual| ≤ 1.0pp clean PASS, breach
within 1 SE of the boundary = PROVISIONAL PASS, beyond = FAIL;
(iii) variant sign check: SHRINK dev 1X2 LL ≤ Gate Zero's in at
least half the dev seasons (≥2 of 3). Both-pass: lower pooled
virgin 1X2 LL ships; ties → simpler arm. Gates never move after
a result is seen; FAIL is a valid outcome. The virgin is small
(n=66), so leg (ii)'s SE band is wide — the gate is applied as
written, not softened (BRIEF).

Halves presentation via the frozen goals constant 0.4387
(FEATURES.md). Predictions-only: no IN odds/settlement source
in-system.

Known calibration risk (recorded, not adjusted): trait
reliability is only moderate (split-half r 0.608 / 0.462) and
season-to-season correlations are weak-to-moderate, while the
goals level ROSE across the dev era (2.579 → 3.331 → 3.182 in the
last two dev seasons) — the expanding fit chases a moving level
with modest team signal; the dev gate will judge that as frozen.
Virgin-season goals/match (3.045, inventory only) sits −0.05
below the dev scored mean (3.093), and the virgin has a different
format (10 teams, split groups) from every dev season. No level
adjustment is made — the gates are frozen and the virgin is read
once.
