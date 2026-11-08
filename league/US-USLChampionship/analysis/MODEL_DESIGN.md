# Phase 4 — Model Design: US-USLChampionship Candidates

Rules of construction are inherited from the J1/US-MLS design: every
candidate names its proven production/J1 reference, states what stays
identical, and lists only the changes justified by USL EDA. Features may
come only from `FEATURES.md` §1 and architectural components from §2. Each
league has its own engine under `league/US-USLChampionship/engine/`.

## Shared validation frame (all candidates)

- **Dev**: walk-forward over 2022–2024 (n=1,318). 2021 is warm-up /
  initial training and is never scored. Count markets predict then update
  per match. Goals use season-blocked expanding fits, as in G-J1/G-US.
- **Virgin**: season **2025**, complete, **n = 375**, read **ONCE** and
  only for arms that pass the dev gate. If no arm passes dev, the virgin
  is NOT read. Season **2026** is reserved and never read in this build;
  it is still in progress in the warehouse.
- **Baselines**: league base rate (prior-seasons over-rate at the primary
  line, constant within season) and naive trailing-10 (count markets) /
  climatology (goals).
- **Gate Zero**: the unmodified reference architecture, fitted per league,
  is itself an arm.
- **Gate legs (verbatim, frozen for every candidate)**: Dev gate — pooled
  dev LL at the primary line beats BOTH baselines, else arm dead, no
  virgin read. Virgin legs — (i) LL ≤ Gate Zero's and ≤ best baseline's;
  (ii) calibration |actual − predicted| ≤ 1.0pp, SE reported, breach
  within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for
  both-pass (variant's dev LL ≤ Gate Zero's in at least half the dev
  seasons). Both-pass: lowest pooled virgin LL ships; ties → simpler arm.
  If Gate Zero fails its own dev gate, the candidate verdict is FAIL
  regardless of variant dev numbers and the virgin is not read.
  (T-USL uses the T-family reading of leg (i) with arm A as reference,
  exactly as in PREREG_T_ITB.)
- **Calibration = actual − predicted** (actual over-rate minus mean
  predicted P(over)) throughout this league.
- **Primary lines** (F10 dev screen): goals OU **2.5** (dev over-rate
  .526), SOT **8.5** (.483), corners **9.5** (.451), cards **4.5**
  (.541), total shots **24.5** (.476; 25.5 would sit at .407).
- **Split format**: regular and playoff matches are in every window and
  are phase-flagged; there is no phase filter. Halves are FT + 1H/2H via
  the frozen F3 constants, presentation only.

## 1. G-USL — goals (1X2 / OU / BTTS / DC)

Reference: production Dixon-Coles pattern via the J1/US-MLS goals engine
(hl=270, rho grid frozen). The X1 observation is **goals-only** — the
blend's documented fallback is the whole fit because xG does not exist
in this league (F6).

Arms: **Gate Zero**; **SHR** — a team with fewer than 8 training matches
has its lambda shrunk 50% toward the fit's league-mean lambda (exactly
the G-US construction). This addresses thin-history teams, including
Lexington SC entering the VIRGIN season 2025 with zero prior matches in
this corpus (F4). No X3 arm (no xG). No X2 offset (no mover population).

## 2. S-USL — shots on target

Reference: `model_sot.py` v5 via the J1/US-MLS SOT engine (joint ridge
Poisson plus total-shots component, Beta-Binomial ratio, naive ensemble;
NB r = 79.94 frozen). The v5 total-shots input comes from the stats feed,
which is complete here; the shotmap-derived quality inputs of the MLS
build do not exist.

Arms: **Gate Zero**; **RS** — ratio prior 200 → 20,000 (the
ridge_shrink arm). No X4/X6 arms (dropped by design, F6).

## 3. C-USL — corners

Reference: `model_corners_v3` via the J1/US-MLS corners engine (ratings +
NB total + territorial multiplier).

Arms: **Gate Zero** with X9 production covariates (possession + big
chances); **X7** — box-touch multiplier, minimum-8 trailing rule with
Gate Zero fallback during the coverage ramp (F8).

## 4. K-USL — cards (unified yellows)

Reference: `model_cards.py` via the J1/US-MLS cards engine. Target is
unified yellows from the **stats feed** (F5 — the events feed is the
broken one in this league). Primary line **4.5**.

Arms: **Gate Zero**; **X8** — referee covariate (F7: r = .378, coverage
92–99% in dev/virgin). It must beat Gate Zero on dev; fixtures without a
named referee fall back to the base arm, with no imputation. The live
pipeline must confirm referee publication pre-match; warehouse snapshots
alone do not prove that condition.

## 5. T-USL — total shots

Reference: the shots family via the J1/IT-SerieB `total_shots` engine.

Arms: **A** — v1 pattern; **B** — v2 pattern (+ level layer, M̄ frozen
at the USL dev mean); **C** — E9 trailing-r mechanism arm. Tuning season
2022 (ridge lambda, r_A, arm B's level-layer cell chosen there only);
gate pool = 2023–2024 pooled, exactly as the T-family preregs. Primary
line **24.5** (F10). Shots dispersion is 1.464 (F9), the highest count
dispersion in the league — the C arm's question is live.

## 6. Global forbidden list

No candidate may use half-share modelling, lineup/absence features,
trailing finishing/conversion/on-target-rate form covariates, two-stage
generative SOT distributions, post-match snapshots (`content.table`,
`h2h`, `teamForm`), conference features, an imported mover offset, or a
feature without a USL reliability check. Any divergence from the named
reference requires a written USL justification here and a pass through
the league's own gate.
