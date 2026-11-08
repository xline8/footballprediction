# Step 6 — Model Design: FI-Ykkonen

Feasibility matrix: **goals — target exists in every season**
(1,730/1,730 FT scores). **SOT / corners / total shots / yellows —
no target exists in any season** (stats feed 0/1,730, shotmap
0/1,730, period splits 0/1,730; cards additionally: zero plain
Yellow events in the whole corpus, referee 0/1,730). **Only G-FI
is buildable.** S/C/K/T are not-buildable on feasibility grounds
(see their prereg files and verdict files); the split was not moved
to manufacture a window for them.

Windows frozen for the built candidate (PROPOSED, not frozen —
Fase 3 is held pending the split decision below): virgin = **2025**
(complete, 162 matches — read ONCE, only for dev-passing arms).
2026 (in progress, 162) is untouched as confirmatory reserve. All
rows are ordinary rows (kakkonen_a/b/c, promotion groups, playoffs,
ykkonen, championship, relegation phase flags carried, never
filtered), per the frozen phase rule in DATA_UNDERSTANDING.md.

Implementation divergence from the FI production references, recorded
pre-fitting: the production engine is not runnable from the bundle,
so the G-FI engine is a port of the FI reference `dc.py` /
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
| G-FI goals | Dixon-Coles Poisson, goals-only (X1 fallback): attack/defence ratings + home advantage, sweep fit, rho grid, score matrix to 10 goals | SHRINK (n<6 prior in-league matches ⇒ attack/defence exponents scaled by n/6 at prediction); X2 (SHRINK + entrant offset g_log −0.182 / c_log +0.223, dev-measured, clamped) | 2021 | 2022–2024 (n=1,010), season-blocked expanding fit | 1X2 LL/RPS + OU 2.5 |
| S-FI SOT | — not-buildable | — | — | — | — |
| C-FI corners | — not-buildable | — | — | — | — |
| K-FI cards | — not-buildable | — | — | — | — |
| T-FI total shots | — not-buildable | — | — | — | — |

X2 entrant offset is **carried** (EDA F4: 22 dev transitions, mean
GF −0.182 / GA +0.235, consistent signs — same direction as the
FI-Veikkausliiga precedent −0.358 / +0.263, opposite to NO where it
was dropped). SHRINK is retained as the variant arm; note it is
expected to be numerically near-inert under season-blocked
prediction (any team present in a prior season has ≥22 prior
matches, so n<6 never binds for a team with a fitted rating; teams
with no fitted rating sit at league mean with exponents 0.0, which
scaling leaves at 0.0) — same observation as CH/NO. It is run and
reported anyway. X2 is the arm that actually differs in this
league, because Kakkonen churn puts ~10 fresh entrants per season
into the scored window.

Gate legs (identical program-wide, frozen verbatim in the prereg):
dev gate — pooled dev 1X2 LL, RPS and OU2.5 LL of an arm must beat
BOTH baselines (climatology; naive trailing-10), else the arm is
dead and the virgin is NOT read for it; if Gate Zero fails dev,
variants are moot, verdict FAIL. Virgin legs — (i) LL ≤ Gate Zero's
and ≤ each baseline's (1X2 and OU2.5); (ii) calibration |mean
predicted − actual| ≤ 1.0pp clean PASS, breach within 1 SE of the
boundary = PROVISIONAL PASS, beyond = FAIL; (iii) variant sign
check: SHRINK/X2 dev 1X2 LL ≤ Gate Zero's in at least half the dev
seasons (≥2 of 3). Both-pass: lower pooled virgin 1X2 LL ships;
ties → simpler arm. Gates never move after a result is seen; FAIL
is a valid outcome.

Halves presentation via the frozen goals constant 0.4463
(FEATURES.md). Predictions-only: no FI odds/settlement source
in-system.

Known risks (recorded, not adjusted):
- **Cross-group identification (EDA F8).** The pooled DC rating
  anchors the three Kakkonen groups together on 22 cross-group
  matches (all 2023) plus the 2024 single table. Group C runs
  ~0.35–0.60 goals/match below group B. If the weak anchoring
  mis-rates cross-group strength, the dev gate (which pools all
  three groups) may still pass while the virgin — a single table
  where every team meets — exposes it. The calibration leg (ii)
  will judge that as frozen. No group adjustment is made — the
  gates are frozen and the virgin is read once.
- **2024 split-phase scoring (EDA F7).** The 30 championship /
  relegation matches in dev score 4.33 goals/match vs 3.33 in the
  regular phase. They are ordinary rows, kept, never filtered;
  a model fitted on dev-era scoring may over-predict virgin
  totals if the split-phase mix differs. The calibration leg (ii)
  will judge that as frozen.
- **Virgin size.** Virgin 2025 is n=162 — small, so the gate's
  sampling-noise band is wide; apply the gate as written, do not
  soften it (per the brief).

## The Kakkonen/Ykkönen break — split options (decision: Jarvis)

The brief split (dev ≤ 2024, virgin 2025) puts 3 of 4 dev seasons
in a different competition from the virgin. The evidence:

| Fact | Number | Source |
|---|---|---|
| Same tier (tier 3) both eras | — | Fase 0 |
| Ykkönen 2024 teams with Kakkonen history | 11/12 (10/12 in 2023) | EDA F9 |
| Regular-phase level, Kakkonen 2023 vs Ykkönen 2024 | 3.329 vs 3.326 goals/match | EDA F7 |
| Halves constant by era | 0.4445 vs 0.4594 | EDA F3 |
| Trait reliability by era | GF 0.610/0.564, GA 0.660/0.680 | EDA F2 |
| Season-to-season trait carry across the break (2023→2024) | GF 0.33 / GA 0.30 (10 teams) | EDA F2 |
| Cross-group matches anchoring Kakkonen groups | 22 in dev era, all 2023 | EDA F8 |
| Kakkonen group level gap (B vs C, 2022–2023) | 3.639 vs 3.034 goals/match | EDA F8 |
| X2 transitions under each option | 22 (dev ≤ 2024) vs 2 (dev = 2024) | EDA F4 |

**Option A — dev ≤ 2024 as briefed** (warm-up 2021, scored
2022–2024, n=1,010; virgin 2025). Pros: the frozen gates run as
written (multi-season dev, season-blocked expanding fit, leg-iii
sign check over 3 scored seasons); X2 is measurable (22
transitions); the break is a format/identification problem, not a
level problem (same tier, 11/12 continuity, regular-phase scoring
identical, halves and reliability stable across eras). Cons: 848
of 1,010 scored matches are three-group Kakkonen; cross-group
ratings rest on 22 matches; group C is a different level; the
2024 split phases (30 matches, 4.33 g/m) enter dev.

**Option B — dev = 2024 only** (n=162, one season; virgin 2025).
Pros: a single coherent competition, every team plays every other.
Cons: the frozen gates cannot run as written — no multi-season dev,
no season-blocked expanding fit, no leg-iii sign check over ≥2 of
3 seasons; n=162 dev is too small to fit DC ratings with any
precision; X2 unmeasurable (2 transitions); the virgin (n=162)
would be judged against a one-season fit. This option needs a
rewritten gate protocol, which is a larger deviation than the
identity break itself.

**Option C — re-scope / cancel.** E.g. treat Kakkonen as a separate
league with no virgin, or drop FI-Ykkonen from the program. Only
if Jarvis judges the identity break fatal.

**Recommendation (Muse-2, evidence-based; decision stays with
Jarvis): Option A.** The measured break is real but bounded: it
changes format and cross-group identification, not the level, the
teams, the halves constant, or trait reliability — and the dev
gate is designed to fail a model whose pooled ratings do not
generalise. Option B destroys the gate protocol to fix a problem
the gate itself is built to detect. If Jarvis picks A, Fase 3
prereg freezes dev ≤ 2024 with the break and the two risks above
recorded verbatim; if B or C, the prereg and gates must be
rewritten before any fitting.
