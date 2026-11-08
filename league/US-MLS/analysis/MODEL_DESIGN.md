# Phase 4 — Model Design: US-MLS Candidates

Rules of construction are inherited from the AT/J1 design: every candidate
names its proven production/J1 reference, states what stays identical, and
lists only the changes justified by MLS EDA. Features may come only from
`FEATURES.md` §1 and architectural components from §2. Each league has its
own engine under `league/US-MLS/engine/`.

## Shared validation frame (all candidates)

- **Dev**: walk-forward over 2022–2024. 2021 is warm-up / initial training and
  is never scored. Count markets predict then update per match. Goals use
  season-blocked expanding fits, as in G-J1/G-AT.
- **Virgin**: season **2025**, complete, **n = 540**, read **ONCE** and only
  for arms that pass the dev gate. If no arm passes dev, the virgin is NOT
  read. Season **2026** is reserved and never read in this build; its
  warehouse inventory is regular slate only and playoffs are absent.
- **Baselines**: league base rate (prior-seasons over-rate at the primary line,
  constant within season) and naive trailing-10 (count markets) / climatology
  (goals).
- **Gate Zero**: the unmodified reference architecture, fitted per league,
  is itself an arm.
- **Gate legs (verbatim, frozen for every candidate)**: Dev gate — pooled dev
  LL at the primary line beats BOTH baselines, else arm dead, no virgin read.
  Virgin legs — (i) LL ≤ Gate Zero's and ≤ best baseline's; (ii) calibration
  |mean P(over) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL
  PASS; (iii) dev per-season sign check for both-pass (variant's dev LL ≤ Gate
  Zero's in at least half the dev seasons). Both-pass: lowest pooled virgin LL
  ships; ties → simpler arm. If Gate Zero fails its own dev gate, the candidate
  verdict is FAIL regardless of variant dev numbers and the virgin is not read.
- **Primary lines**: goals OU **2.5** (dev over-rate **0.584**), SOT **8.5**
  (**0.558**), corners **9.5** (**0.514**), cards **4.5** (**0.402**), total
  shots **25.5** (**0.492**).
- **Split format**: regular and playoff matches are in every window and are
  phase-flagged; there is no phase filter. Halves are FT + 1H/2H via the
  frozen F3 constants, presentation only.

## 1. G-US — goals (1X2 / OU / BTTS / DC)

Reference: production Dixon-Coles plus blend via the J1/AT goals engine
(hl=270, blend 0.5, rho grid frozen). The blend uses X1, with the documented
goals-only fallback for the 0.8% of 2021 matches without xG.

Arms: **Gate Zero**; **SHR** — a team with fewer than 8 training matches has
its lambda shrunk 50% toward the fit's league-mean lambda; this addresses
expansion-club entry variance, including San Diego entering the virgin season
with zero history; **X3** — SHR plus the set-play decomposition tilt, built as
G-J1's X3 arm. No X2 offset exists because MLS has no relegation/mover
population.

Forbidden: halves modelling, finishing/form, absence features, snapshots, and
imported tier offsets.

## 2. S-US — shots on target

Reference: `model_sot.py` v5 via the J1/AT SOT engine (joint ridge Poisson plus
total-shots component, Beta-Binomial ratio, naive ensemble; NB **r = 79.94**
frozen).

Arms: **Gate Zero**; **RS** — ratio prior 200 → 20,000; **X4** — xG/shot
input; **X6** — xGOT/shot input, era-guarded from **2024-01-01**. X4 and X6 are
constructed exactly as S-J1's arms. X6 is an arm only because its MLS
reliability is **r = 0.355** and its era is short; the dev gate decides.

Forbidden: halves modelling, finishing/conversion features, standalone
on-target-rate covariates, defensive xGOT, absence features, and two-stage
generative distributions.

## 3. C-US — corners

Reference: `model_corners_v3` via the J1/AT corners engine (ratings + NB total +
territorial multiplier).

Arms: **Gate Zero** with X9 production covariates (possession + big chances);
**X7** — box-touch multiplier, using the minimum-8 trailing rule and falling
back to Gate Zero when coverage is insufficient. The rationale is box-touch
correlation **.513** versus possession **.343**, with box-touch reliability
**r = .711/.695**.

## 4. K-US — cards (unified yellows)

Reference: `model_cards.py` via the J1/AT cards engine (team card ratings and
count distribution; referee not used in production). Target is unified
yellows from the stats feed. Primary line **4.5**.

Arms: **Gate Zero**; **X8** — referee covariate. It must beat Gate Zero on
dev; fixtures without a named referee fall back to the base arm, with no
imputation. Coverage is 0% in 2021 (warm-up only) and approximately 96–99%
in dev/virgin seasons. The live pipeline must confirm referee publication
pre-match; warehouse snapshots alone do not prove that condition.

## 5. T-US — total shots

Reference: the shots family via the J1/AT `total_shots` engine.

Arms: **A** — v1 pattern; **C** — E9 trailing-r mechanism arm. This is built
ahead of the top-5 verdict under the same provenance rule as AT §5: the
prospective top-5 trial is untouched, and its result does not contaminate this
league's separate dev/virgin fitting.

## 6. Global forbidden list

No candidate may use half-share modelling, lineup/absence features, trailing
finishing/conversion/on-target-rate form covariates, defensive xGOT traits,
two-stage generative SOT distributions, post-match snapshots (`content.table`,
`h2h`, `teamForm`), an imported mover offset, or a feature without an MLS
reliability check. Any divergence from the named reference requires a written
MLS justification here and a pass through the league's own gate.
