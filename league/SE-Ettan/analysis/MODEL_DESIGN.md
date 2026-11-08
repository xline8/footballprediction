# Step 6 — Model Design: SE-Ettan

Feasibility matrix: goals — target exists in all seasons, trait
reliable (F2: split-half r 0.562 dev / 0.703 scored window for
goals-for), dev scored window 2022–2024 (n=1,440) plus a partial
warm-up 2021 (n=262, no events). SOT / corners / total shots /
yellows — targets exist in NO season (the stats feed is 0% in
2021–2025; the stats era never starts); there is no dev season, no
warm-up season, no halves constant, and no measurable trait
reliability for any of them. **Only G-SE is buildable. S/C/K/T are
not-buildable under the frozen split** (the split is not moved:
re-splitting after seeing the era break would be post-hoc window
shopping). Cards additionally has the F5 caveats: event-derived
yellows exist and are moderately reliable (r 0.549), but there is no
stats feed to validate them against, no events in 2021, and no
referee data at all — revisiting K needs a program-level decision
from Jarvis (adopt event yellows as the target by definition, and
re-split dev to start 2022), which is NOT made here. Total shots is
the FI case in its strongest form: not a definition break within a
dev window, but the complete absence of a dev window.

Windows frozen for the built candidate: virgin = **2025** (complete,
480 matches — read ONCE, only for the dev-passing arm). 2026 (480
matches in the built CSVs) is untouched. Implementation divergence
from the FI production references, recorded pre-fitting: the
production engines are not runnable in this bundle, so the G-SE
engine is a minimal, documented port of the reference *pattern*
(Dixon-Coles for goals), written in numpy/scipy (no sklearn exists
in this environment). Constants not carried over are listed in the
prereg.

| Candidate | Gate Zero pattern | Variant arms | Warm-up | Dev scored | Primary line |
|---|---|---|---|---|---|
| G-SE goals | Dixon-Coles Poisson (goals-only, X1 fallback): attack/defence ratings + home advantage fitted by Poisson likelihood (L-BFGS, sum-to-zero), rho from grid (0, −0.05, −0.10, −0.15) by fit log-likelihood, score matrix to 10 goals | SHRINK only (X2 rejected: no entrant tilt, F4 — GF −0.013 / GA +0.081 over 27 dev transitions). NO ENTRANT arm, unlike QA. | 2021 (partial, 262 played, no events) | 2022–2024 (n=1,440), season-blocked expanding fit | 1X2 LL/RPS + OU 2.5 |
| S-SE SOT | — not-buildable | — | — | — (no stats season in any season) | — |
| C-SE corners | — not-buildable | — | — | — (no stats season in any season) | — |
| K-SE cards | — not-buildable | — (X8 data absent in every season; event-yellows evidence preserved in EDA F5 for a future Jarvis decision) | — | — (no cards target under the canonical definition; event-derived yellows have no complete dev window — 2021 has no events) | — |
| T-SE total shots | — not-buildable | — | — | — (no stats season in any season) | — |

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
(goals 0.4385 only; no count-market constant exists).
Predictions-only: no SE odds/settlement source in-system.

Format note for the engine: two independent groups (Norra/Södra,
16 teams each) with no cross-group matches in the feed — ratings
are fitted per team across the matches they actually played, which
are all within-group. No group term is fitted (see EDA F1); if the
dev gate shows a systematic Norra/Södra level gap the engine
cannot absorb, that is a Phase 4 finding, not a reason to add a
term post-hoc.
