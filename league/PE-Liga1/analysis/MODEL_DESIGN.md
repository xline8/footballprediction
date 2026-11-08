# Step 6 — Model Design: PE-Liga1 Candidates

Rules of construction are the programme's: every candidate names
its proven reference, states what stays identical, and lists only
the changes this league's EDA justifies. One league = one engine
under `league/PE-Liga1/engine/<market>/`. Features consumed are
only FEATURES.md §1 (+ §2 components). Gates are the programme's,
identical everywhere, and are frozen per candidate in
`league/PE-Liga1/prereg/PREREG_<X>_PE.md` **before any fitting**.

**Shared validation frame**

- Corpus: regular phase, non-awarded (PREPROCESSING rule 4).
- **Windows (G/S/C/T):** seed = 2021 blocks (Fase 1 + Fase 2,
  n = 234, training only); dev eval = 2022-Apertura … 2024-Clausura
  (6 blocks, n = 982); **virgin = the full 2025 calendar year**
  (Apertura + Clausura, n = 323), the last complete season, read
  ONCE and only for arms passing the dev gate. 2026 is the reserved
  confirmatory window (in progress) and is not read anywhere.
- **Windows (K, cards era — EDA F-feed-1):** the cards reference
  harness is an online walk-forward, so K uses its own blocking:
  seed = 2023 - Apertura (n = 165); dev eval = 2023 - Clausura …
  2024 - Clausura (3 blocks, n = 475); virgin = 2025 (n = 323).
  (Refined from the design-stage sketch — seed 2023 / dev 2024 —
  to the reference harness's exact form, recorded here before any
  fitting and frozen in PREREG_K_PE.)
- Fits are block-blocked walk-forward: for target block S, fit on
  all corpus matches strictly before S's first match date.
- Targets: goals = FT score; SOT = stats-feed `ShotsOnTarget` sum
  (scored rows = stats rows only); corners likewise; cards =
  event-unified yellows incl. second yellows (F-feed-1); total
  shots = the unified target of F-feed-2.
- Primary lines (dev distributions, EDA): OU 2.5; SOT 8.5;
  corners 9.5; cards 4.5; total shots 19.5.
- Gate legs (all candidates, mechanical): dev gate = pooled dev LL
  at the primary line beats BOTH baselines (league base rate +
  naive trailing-10; goals: 1X2 LL + RPS beat climatology and OU2.5
  LL beats base rate). Virgin legs: (i) LL ≤ Gate Zero's (arm A's
  for T) AND ≤ both baselines'; (ii) calibration |actual − predicted|
  ≤ 1.0pp clean PASS, breach within 1 SE of the boundary =
  PROVISIONAL PASS, beyond = FAIL (SE = sd(p_i − y_i)/√n); (iii)
  per-block dev sign check for variant arms (LL ≤ reference in at
  least half the dev blocks). Both-pass → lower virgin LL ships;
  tie → simpler arm. **If Gate Zero (arm A) fails its dev gate,
  variants are moot, verdict FAIL, virgin NOT read.** Gates never
  move after results.

## G-PE — goals (Dixon-Coles, goals-only)

Reference: production `model_v2.py` DC pattern (hl = 270, 14 sweeps,
damping 0.7, +0.25 smoothing, MAXG = 10, rho grid
{0, −0.05, −0.10, −0.15}) as ported for CO-A. Identical except:
observation is goals-only throughout (X1-reduced — no xG exists).
Arms: **Gate Zero**; **X2** = Gate Zero with entrant ratings
replaced by the frozen F4 offsets in a club's entry year
(`a = −0.0645`, `d = +0.1024`). No SHRINK arm: the only
few-prior clubs at any block start are entrants at exactly 0
priors, where shrinkage is identical to Gate Zero's unseen rule
(CO-A precedent) — X2 is the registered answer to that concern.
No altitude arm (R-alt).

## S-PE — shots on target (v5 pattern)

Reference: `model_sot.py` v5 (joint ridge Poisson ratings + NB +
Beta-Binomial ratio, 50/50 naive ensemble), ported as in the
programme's S engines. Its total-shots input uses the **unified**
shots target (F-feed-2). Arms: **Gate Zero**; **RS** = Gate Zero
with the ratio prior raised to 20,000 (ratio ≈ league constant —
the J1 §2 test of the ratio component; S traits here are moderate,
0.598/0.536, and no X4/X6 quality arm can exist: no shotmap).
The RS prior value follows the programme's RS ports.

## C-PE — corners (model_corners_v3 pattern)

Reference: production corners (decay-weighted base rates + rolling
relative factors + NB total + territorial multiplier
`exp(beta·z)` clamped [0.70, 1.43]). Arms: **Gate Zero** (X9
covariates); **X7** = Gate Zero plus the opp-box touches component
(X7, F2: corr 0.571 > possession 0.447), fitted as the reference
X7 arm fits its beta (β = 0 collapses X7 to Gate Zero numerically).

## K-PE — cards (model_cards pattern, cards era 2023+)

Reference: production cards pattern (ratings + NB total on the
candidate's yellow target). Target: event-unified yellows incl.
second yellows (F-feed-1 — the stats-vs-events artefact is present
and era-flipped; the stats target is additionally unusable because
rich stats are absent from every dev Clausura block). Arms:
**Gate Zero**; **X8** = Gate Zero plus the referee multiplier
(X8, F8: r = 0.769). Windows are the cards-era windows above
(online walk-forward, seed 2023 - Apertura).

## T-PE — total shots (shots family, unified target)

Reference: the experiments shots family / J1 T engine. Target: the
unified shots total of F-feed-2 (blocked shots excluded — the only
homogeneous quantity the feed carries). Arms: **A** = v1 pattern;
**B** = v2 level layer (M_BAR frozen at this league's dev pooled
unified mean, 19.727); **C** = E9 trailing-r. Built ahead of the
top-5 prospective verdict by the programme's standing user order;
that trial is untouched.

## Halves presentation

On PASS, shipped predictions carry FT + 1H/2H derived with the
frozen constants of F3 (goals 0.4377, SOT 0.4611, corners 0.4817,
total shots 0.4662, cards 0.3818) — presentation only, never gated.
