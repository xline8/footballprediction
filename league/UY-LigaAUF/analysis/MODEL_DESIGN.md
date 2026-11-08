# Step 6 — Model Design: UY-LigaAUF

Feasibility matrix: goals — target exists all seasons, trait reliable
(F2: split-half r 0.588 attack / 0.809 defence), dev scored window
2022–2024 (n=895). SOT / corners / total shots / yellows — targets
exist in NO season under any source (stats feed 0% in 2021–2026);
cards additionally has a target-definition break in the event feed
(plain Yellows only from 2023) and zero referee data. **Only G-UY is
buildable. S/C/K/T are not-buildable under the frozen split** (the
split is not moved: re-splitting after seeing the era break would be
post-hoc window shopping).

Windows frozen for the built candidate: virgin = **2025** (complete,
300 matches — read ONCE, only for the dev-passing arm). 2026
(in progress, 281) is untouched. Implementation divergence from the
FI production references, recorded pre-fitting: the production engines
are not runnable in this bundle, so the G-UY engine is a minimal,
documented port of the reference *pattern* (Dixon-Coles for goals),
written in numpy/scipy. Constants not carried over are listed in the
prereg.

| Candidate | Gate Zero pattern | Variant arms | Warm-up | Dev scored | Primary line |
|---|---|---|---|---|---|
| G-UY goals | Dixon-Coles Poisson (goals-only, X1 fallback): attack/defence ratings + home advantage fitted by Poisson likelihood (L-BFGS, sum-to-zero), rho from grid (0, −0.05, −0.10, −0.15) by fit log-likelihood, score matrix to 10 goals | ENTRANT (X2 adopted, F4): teams in their entrant season get the dev-measured entrant offset (attack −0.1178, defence −0.1188, frozen in the prereg; 9 dev transitions, GF −0.128 / GA +0.145) | 2021 | 2022–2024 (n=895), season-blocked expanding fit | 1X2 LL/RPS + OU 2.5 |
| S-UY SOT | — not-buildable | — | — | — (no stats target in any season) | — |
| C-UY corners | — not-buildable | — | — | — (no stats target in any season) | — |
| K-UY cards | — not-buildable | — (X8 data absent in dev; event Yellows only from 2023 = definition break) | — | — (no consistent cards target in dev, either source) | — |
| T-UY total shots | — not-buildable | — | — | — (no stats target in any season) | — |

Gate legs (identical program-wide, frozen verbatim in the prereg):
dev gate — pooled dev LL at the primary line (goals: 1X2 LL, RPS and
OU LL legs) beats BOTH baselines (league base rate / climatology;
naive trailing-10), else the arm is dead and the virgin is NOT read
for it; if Gate Zero fails dev, variants are moot, verdict FAIL.
Virgin legs — (i) LL ≤ Gate Zero's and ≤ best baseline's; (ii)
calibration |mean predicted − actual| ≤ 1.0pp clean PASS, breach
within 1 SE of the boundary = PROVISIONAL PASS, beyond = FAIL;
(iii) variant sign check: variant dev LL ≤ Gate Zero's in at least
half the dev seasons (goals only; count candidates are not-buildable
so (iii) is vacuous for them). Both-pass: lower pooled virgin LL
ships; ties → simpler arm. Gates never move after a result is seen;
FAIL is a valid outcome.

Halves presentation via the frozen constant in FEATURES.md
(goals 0.4276 only; no count-market constant exists).
Predictions-only: no UY odds/settlement source in-system.
