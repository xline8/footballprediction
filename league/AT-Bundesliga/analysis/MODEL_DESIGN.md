# Phase 4 — Model Design: AT-Bundesliga Candidates

Rules of construction inherited from `league/J1/analysis/MODEL_DESIGN.md`:
every candidate names its proven production/J1 reference, states what
stays identical, and lists only the changes this league's EDA justifies
(each tied to a numbered finding). Features only from FEATURES.md §1.
Per-league engine under `league/AT-Bundesliga/engine/<market>/`, seeded
from the J1 engine of the same market (itself seeded from production).

## Shared validation frame (all candidates)

- **Dev**: walk-forward over seasons 2022/2023–2024/2025 (2021/2022 is
  warm-up / initial training, never scored). Count markets: per-match
  predict-then-update. Goals: season-blocked expanding fits (one fit
  per target season from matches strictly before it), as G-J1.
- **Virgin**: season **2025/2026** (complete, n=195), read **ONCE**, only
  for arms that pass the dev gate; if NO arm passes dev, the virgin is
  NOT read. Season 2026/2027 is in progress and reserved as the
  confirmatory window — never read in this build.
- **Baselines**: league base rate (prior-seasons over-rate at the
  primary line, constant within a season) and naive trailing-10 (count
  markets) / climatology (goals).
- **Gate Zero**: the unmodified reference architecture, fitted per
  league, is itself an arm.
- **Gate legs (verbatim, frozen for every candidate)**: Dev gate —
  pooled dev LL at the primary line beats BOTH baselines, else arm
  dead, no virgin read. Virgin legs — (i) LL ≤ Gate Zero's and ≤ best
  baseline's; (ii) calibration |mean P(over) − actual| ≤ 1.0pp, SE
  reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev
  per-season sign check for both-pass (variant's dev LL ≤ Gate Zero's
  in at least half the dev seasons). Both-pass: lowest pooled virgin
  LL ships; ties → simpler arm. If Gate Zero fails its own dev gate,
  the candidate verdict is FAIL regardless of variant dev numbers and
  the virgin is not read.
- **Primary lines** (from the dev distribution): goals OU 2.5
  (dev over-rate 53.7%), SOT 8.5 (48.2%), corners 9.5 (51.7%), cards
  4.5 (41.0%), total shots 24.5 (50.1%).
- **Split format**: split/playoff matches are in every window (Phase 1
  §1); no phase filter anywhere. Halves presentation: FT + 1H/2H via
  the frozen F3 constants, presentation only.

## 1. G-AT — goals (1X2 / OU / BTTS / DC)
Reference: production Dixon-Coles + blend (J1 engine `goals/` pattern,
hl=270, blend 0.5, rho grid — frozen constants as G-J1).
Arms: **Gate Zero**; **SHR** — thin-team shrinkage: for a team with
fewer than 8 training-window matches (promoted clubs at season entry),
its predicted lambdas are shrunk 50% toward the league-mean lambda
(the template-sanctioned pre-registered response to the G-J2
post-mortem; F4 records why no X2 offset exists here); **X3** — SHR
plus the set-play decomposition tilt (X3, F5 r=0.477), constructed
exactly as G-J1's X3 arm.
Forbidden: halves modelling (F3), finishing/form (F6), absence (F10),
snapshot features, imported tier offsets (R14).

## 2. S-AT — shots on target
Reference: `model_sot.py` v5 via the J1 engine `sot/` (joint ridge
Poisson + total-shots component + Beta-Binomial ratio + naive
ensemble, NB r=79.94 frozen).
Arms: **Gate Zero**; **RS** — ratio prior P 200 → 20,000 (tests F6:
team SOT-rate trait is NOISE here too, r=−0.114); **X4** — xG/shot
quality input (X4, F6 r=0.480), constructed exactly as S-J1's X4 arm.
**No X6 arm**: the xGOT trait failed its reliability check in this
league (F7, r=0.273) and is dropped at the feature step.
Forbidden: as G-AT plus defensive xGOT (R5), two-stage generative
distributions (V11 stands).

## 3. C-AT — corners
Reference: `model_corners_v3` via the J1 engine `corners/` (ratings +
NB total + territorial multiplier).
Arms: **Gate Zero** (X9 covariates: possession + big chances);
**X7** — box-touch multiplier (X7, F9: trait r=0.945/0.813, corr 0.546
vs possession 0.407), constructed as C-J1's X7 arm with the min-8
trailing rule absorbing the pre-2024/2025 coverage ramp (arm falls
back to Gate Zero where its window is thin).

## 4. K-AT — cards (yellows)
Reference: `model_cards.py` via the J1 engine `cards/` (team card
ratings, count distribution; referee not used in production).
Target: unified yellows (stats feed, 100% coverage — no provenance
exception needed). Primary line 4.5.
Arms: **Gate Zero**; **X8** — referee covariate (X8, F8 r=0.547;
coverage 91.8% in the virgin season). Binding conditions as K-J1:
must beat Gate Zero on dev; fixtures without a named referee fall
back to the base arm (no imputation). Operational note as K-J1:
warehouse records are post-match snapshots; pre-match referee
publication cannot be proven from them; the fallback is the rule.

## 5. T-AT — total shots
Reference: the shots family via the J1 engine `total_shots/`.
Arms: **A** — v1 pattern (ratings + NB + naive ensemble, frozen r
from the dev fit); **C** — E9 mechanism (NB r from a trailing window,
league-level). Built ahead of the top-5 prospective verdict under the
same user order recorded for T-J1 (different corpus, different virgin
window, no shared fitting; the top-5 trial is untouched).

## 6. Global forbidden list
Inherited from J1 MODEL_DESIGN §7 as amended (per-league engines are
the rule; divergence only as this design justifies, through this
league's gate). Half-share modelling, absence features, finishing /
conversion / on-target-rate form features, two-stage generative SOT,
post-match snapshot features, and any feature without a reliability
check are forbidden for every candidate above.
