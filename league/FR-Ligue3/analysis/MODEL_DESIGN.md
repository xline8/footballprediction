# Step 6 — Model Design: FR-Ligue3

Feasibility matrix: **goals — target exists in every season**
(1,570/1,570 FT scores). **SOT / corners / total shots / yellows —
no target exists in any season** (stats feed 0/1,570, shotmap
0/1,570, period splits 0/1,570). **Only G-FR is buildable.**
S/C/K/T are not-buildable on feasibility grounds (see their prereg
files and verdict files); the split was not moved to manufacture a
window for them. Cards additionally: event plain-Yellow events exist
only from 2023/2024 (target-definition break across dev) and referee
coverage is 0% in every season (no X8 arm).

Windows frozen for the built candidate: virgin = **2025/2026**
(complete, 272 matches — read ONCE, only for dev-passing arms).
2026/2027 (in progress, 108) is untouched as confirmatory reserve.
All rows are ordinary rows (phase flag `main` carried, never
filtered), per the frozen phase rule in DATA_UNDERSTANDING.md.

Implementation divergence from the FI production references, recorded
pre-fitting: the production engine is not runnable from the bundle,
so the G-FR engine is a port of the FI reference `dc.py` /
`arms.py` carried over **verbatim** (iterative sweep optimiser, 14
sweeps, damping 0.7, +0.25 smoothing, home init 0.28, MAXG = 10,
rho grid (0.0, −0.05, −0.10, −0.15) by goals log-likelihood, decay
HL = 270 days), with the harness adapted from the FI `harness.py`
plus the naive trailing-10 baseline as defined in the IL goals
prereg (per-team trailing-10 goals-for means, independent Poissons,
no home advantage). The X1 blend's documented fallback applies
throughout: the observation is goals-only in every match (no xG
exists in this feed), exactly as frozen in the FI prereg. Constants
not carried over are listed in the prereg.

| Candidate | Gate Zero pattern | Variant arms | Warm-up | Dev scored | Primary line |
|---|---|---|---|---|---|
| G-FR goals | Dixon-Coles Poisson, goals-only (X1 fallback): attack/defence ratings + home advantage, sweep fit, rho grid, score matrix to 10 goals | SHRINK (n<6 prior in-league matches ⇒ attack/defence exponents scaled by n/6 at prediction) | 2021/2022 | 2022/2023–2024/2025 (n=884), season-blocked expanding fit | 1X2 LL/RPS + OU 2.5 |
| S-FR SOT | — not-buildable | — | — | — | — |
| C-FR corners | — not-buildable | — | — | — | — |
| K-FR cards | — not-buildable | — | — | — | — |
| T-FR total shots | — not-buildable | — | — | — | — |

X2 entrant offset is dropped pre-fitting (EDA F4: 21 dev
transitions, mean GF −0.010 / GA −0.011, mixed signs — no
systematic tilt). SHRINK is retained as the variant arm; note it is
expected to be numerically inert under season-blocked prediction
(any team present in a prior season has ≥32 prior matches, so n<6
never binds for a team with a fitted rating; teams with no fitted
rating sit at league mean with exponents 0.0, which scaling leaves
at 0.0) — same observation as CH and NO. It is run and reported anyway.

Gate legs (identical program-wide, frozen verbatim in the prereg):
dev gate — pooled dev 1X2 LL, RPS and OU2.5 LL of an arm must beat
BOTH baselines (climatology; naive trailing-10), else the arm is
dead and the virgin is NOT read for it; if Gate Zero fails dev,
variants are moot, verdict FAIL. Virgin legs — (i) LL ≤ Gate Zero's
and ≤ each baseline's (1X2 and OU2.5); (ii) calibration |mean
predicted − actual| ≤ 1.0pp clean PASS, breach within 1 SE of the
boundary = PROVISIONAL PASS, beyond = FAIL; (iii) variant sign
check: SHRINK dev 1X2 LL ≤ Gate Zero's in at least half the dev
seasons (≥2 of 3). Both-pass: lower pooled virgin 1X2 LL ships;
ties → simpler arm. Gates never move after a result is seen; FAIL
is a valid outcome.

Halves presentation via the frozen goals constant 0.4618
(FEATURES.md). Predictions-only: no FR odds/settlement source
in-system.

Known calibration risk (recorded, not adjusted): trait reliability
is weak (split-half r 0.323 / 0.309) and season-to-season team-mean
correlations are weak and mixed, so the expanding fit may lag
churn; the dev gate will judge that as frozen. Virgin-season
goals/match (2.423, inventory only) sits −0.06 below the dev scored
mean (2.484). No level adjustment is made — the gates are frozen
and the virgin is read once.
