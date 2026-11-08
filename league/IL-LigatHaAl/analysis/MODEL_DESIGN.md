# Step 6 — Model Design: IL-LigatHaAl

Feasibility matrix: goals — target exists all seasons, trait reliable
(F2: r 0.86), dev scored window 2022/2023–2024/2025 (n=720). SOT /
corners / total shots / yellows — targets exist ONLY in the stats era
(2025/2026+), i.e. in the virgin season itself and the untouched
reserve; there is no dev season, no warm-up season, no halves constant,
and no measurable trait reliability for any of them. **Only G-IL is
buildable. S/C/K/T are not-buildable under the frozen split** (the split
is not moved: re-splitting after seeing the era break would be post-hoc
window shopping). Cards additionally has no event-feed fallback in dev
(zero plain Yellow events 2021/2022–2024/2025). Total shots is the FI
case in its strongest form: not a definition break within a dev window,
but the complete absence of a dev window.

Windows frozen for the built candidate: virgin = **2025/2026**
(complete, 240 matches — read ONCE, only for the dev-passing arm).
2026/2027 (in progress, 70) is untouched. Implementation divergence
from the FI production references, recorded pre-fitting: the production
engines are not runnable in this bundle, so the G-IL engine is a
minimal, documented port of the reference *pattern* (Dixon-Coles for
goals), written in numpy/scipy (no sklearn exists in this environment).
Constants not carried over are listed in the prereg.

| Candidate | Gate Zero pattern | Variant arms | Warm-up | Dev scored | Primary line |
|---|---|---|---|---|---|
| G-IL goals | Dixon-Coles Poisson (goals-only, X1 fallback): attack/defence ratings + home advantage fitted by Poisson likelihood (L-BFGS, sum-to-zero), rho from grid (0, −0.05, −0.10, −0.15) by fit log-likelihood, score matrix to 10 goals | ENTRANT (X2 adopted, F4): teams in their first season in the corpus get the dev-measured entrant offset (attack/defence shift from the 6 dev transitions, GF −0.358 / GA +0.263, frozen in the prereg) | 2021/2022 | 2022/2023–2024/2025 (n=720), season-blocked expanding fit | 1X2 LL/RPS + OU 2.5 |
| S-IL SOT | — not-buildable | — | — | — (no stats season in dev) | — |
| C-IL corners | — not-buildable | — | — | — (no stats season in dev) | — |
| K-IL cards | — not-buildable | — (X8 data absent in dev) | — | — (no cards target in dev, either source) | — |
| T-IL total shots | — not-buildable | — | — | — (no stats season in dev) | — |

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
(goals 0.4497 only; no count-market constant exists).
Predictions-only: no IL odds/settlement source in-system.
