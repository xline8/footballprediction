# Step 6 — Model Design: SG-PremierLeague

Feasibility matrix: **goals — target exists in every season**
(555/555 FT scores). **SOT / corners / total shots / yellows —
no target exists in any season** (stats feed 0/555, shotmap
0/555, period splits 0/555). **Only G-SG is buildable.**
S/C/K/T are not-buildable on feasibility grounds (see their
prereg files and verdict files); the split was not moved to
manufacture a window for them. Cards additionally: zero
plain-Yellow events in any season (no yellows target at all)
and referee coverage is 0% in every dev season (no X8 arm).

Windows frozen for the built candidate: virgin = **2025/2026**
(complete, 84 matches — small; read ONCE, only for dev-passing
arms, gate applied as written per BRIEF). 2026/2027 (in
progress, 23) is untouched as confirmatory reserve. All rows
are ordinary rows (phase flag `main` carried, never filtered),
per the frozen phase rule in DATA_UNDERSTANDING.md.

Implementation divergence from the FI production references,
recorded pre-fitting: the production engine is not runnable
from the bundle, so the G-SG engine is a port of the FI
reference `dc.py` / `arms.py` (iterative sweep optimiser, 14
sweeps, damping 0.7, +0.25 smoothing, home init 0.28, MAXG =
10, rho grid (0.0, −0.05, −0.10, −0.15) by goals log-likelihood,
decay HL = 270 days), with the harness adapted from the FI
`harness.py` plus the naive trailing-10 baseline as defined in
the IL goals prereg (per-team trailing-10 goals-for means,
independent Poissons, no home advantage). Two documented port
adaptations, both mechanics-preserving: (1) season labels are
split-season strings from 2024/2025, so season ordering uses
the frozen ordered season list, not integer arithmetic;
(2) the X2 arm is not ported at all — X2 was dropped on EDA
evidence (F4), so the engine carries Gate Zero + SHRINK only.
The X1 blend's documented fallback applies throughout: the
observation is goals-only in every match (no xG exists in this
feed), exactly as frozen in the FI prereg.

| Candidate | Gate Zero pattern | Variant arms | Warm-up | Dev scored | Primary line |
|---|---|---|---|---|---|
| G-SG goals | Dixon-Coles Poisson, goals-only (X1 fallback): attack/defence ratings + home advantage, sweep fit, rho grid, score matrix to 10 goals | SHRINK (n<6 prior in-league matches ⇒ attack/defence exponents scaled by n/6 at prediction) | 2021 | 2022, 2023, 2024/2025 (n=364), season-blocked expanding fit | 1X2 LL/RPS + OU 2.5 |
| S-SG SOT | — not-buildable | — | — | — | — |
| C-SG corners | — not-buildable | — | — | — | — |
| K-SG cards | — not-buildable | — | — | — | — |
| T-SG total shots | — not-buildable | — | — | — | — |

X2 entrant offset is DROPPED pre-fitting (EDA F4: 1 dev
transition only, GA sign contradicts the entrant pattern — the
opposite evidence to BY/FI, the same decision as CH/NO/SE).
SHRINK is retained as the variant arm; note it is expected to
be numerically inert under season-blocked prediction (any team
present in a prior season has ≥21 prior matches, so n<6 never
binds for a team with a fitted rating; teams with no fitted
rating sit at league mean with exponents 0.0, which scaling
leaves at 0.0) — same observation as CH/NO/FR/BY. It is run and
reported anyway; the gate decides.

Gate legs (identical program-wide, frozen verbatim in the
prereg): dev gate — pooled dev 1X2 LL, RPS and OU2.5 LL of an
arm must beat BOTH baselines (climatology; naive trailing-10),
else the arm is dead and the virgin is NOT read for it; if
Gate Zero fails dev, variants are moot, verdict FAIL. Virgin
legs — (i) LL ≤ Gate Zero's and ≤ each baseline's (1X2 and
OU2.5); (ii) calibration |mean predicted − actual| ≤ 1.0pp
clean PASS, breach within 1 SE of the boundary = PROVISIONAL
PASS, beyond = FAIL; (iii) variant sign check: SHRINK dev 1X2
LL ≤ Gate Zero's in at least half the dev seasons (≥2 of 3).
Both-pass: lower pooled virgin 1X2 LL ships; ties → simpler
arm. Gates never move after a result is seen; FAIL is a valid
outcome.

Halves presentation via the frozen goals constant 0.4404
(FEATURES.md). Predictions-only: no SG odds/settlement source
in-system.

Known calibration risk (recorded, not adjusted): trait
reliability is strong (split-half r 0.881 / 0.869) and
season-to-season correlations are positive, so the expanding
fit has real signal to track — but the virgin season's
goals/match (3.607, inventory only) sits −0.71 BELOW the dev
scored mean (4.316), the largest dev→virgin level drop in the
program so far, and the virgin is small (n=84, wide sampling
noise, per BRIEF). Dev season levels also swing 3.98–4.52.
No level adjustment is made — the gates are frozen and the
virgin is read once.
