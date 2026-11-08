# Phase 4 — Model Design: NO-Eliteserien Candidates

Rules of construction inherited from `league/J1/analysis/MODEL_DESIGN.md`:
every candidate names its proven production/J1 reference, states what
stays identical, and lists only the changes this league's EDA justifies
(each tied to a numbered finding). Features only from FEATURES.md §1.
Per-league engine under `league/NO-Eliteserien/engine/<market>/`, seeded
from the AT-Bundesliga engine of the same market (itself seeded from
the J1 engine, itself from production), with the line/season retargets
this league's dev distribution requires.

## Shared validation frame (all candidates)

- **Dev**: walk-forward over seasons 2022–2024 (2021 is warm-up /
  initial training, never scored). Count markets: per-match
  predict-then-update. Goals: season-blocked expanding fits (one fit
  per target season from matches strictly before it), as G-J1.
- **Virgin**: season **2025** (complete, n=240), read **ONCE**, only
  for arms that pass the dev gate; if NO arm passes dev, the virgin is
  NOT read. Season 2026 is in progress and reserved as the
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
- **Primary lines** (from the dev distribution — the ladder line whose
  dev over-rate is closest to 50%): goals OU 2.5 (dev over-rate
  60.4%), SOT 8.5 (52.5%), corners **10.5** (48.3%), cards **2.5**
  (60.3%; the next line, 3.5, sits at 33.9% — 2.5 is closer to 50%),
  total shots **26.5** (48.5%).
- **Format**: all matches are regular-season (Phase 1 §1); no phase
  filter anywhere. Halves presentation: FT + 1H/2H via the frozen F3
  constants, presentation only.

## 1. G-NO — goals (1X2 / OU / BTTS / DC)
Reference: production Dixon-Coles + blend (J1 engine `goals/` pattern
via AT, hl=270, blend 0.5, rho grid — frozen constants as G-J1).
Arms: **Gate Zero**; **SHR** — thin-team shrinkage: for a team with
fewer than 8 training-window matches (promoted clubs at season entry),
its predicted lambdas are shrunk 50% toward the league-mean lambda
(the template-sanctioned pre-registered response to the G-J2
post-mortem; F4 records why no X2 offset exists here); **X3** — SHR
plus the set-play decomposition tilt (X3, F5 r=0.577), constructed
exactly as G-J1's X3 arm.
Forbidden: halves modelling (F3), finishing/form (F6), absence (F10),
snapshot features, imported tier offsets (R14).

## 2. S-NO — shots on target
Reference: `model_sot.py` v5 via the J1 engine `sot/` (joint ridge
Poisson + total-shots component + Beta-Binomial ratio + naive
ensemble, NB r=79.94 frozen).
Arms: **Gate Zero**; **RS** — ratio prior P 200 → 20,000 (tests how
much team ratio variation to keep; in this league the on-target-rate
trait is reliable, F6 r=0.477 — unlike J1/AT — so RS is a genuine
two-sided test here); **X4** — xG/shot quality input (X4, F6 r=0.770,
the program's strongest), constructed exactly as S-J1's X4 arm.
**No X6 arm**: the xGOT trait's guarded era starts in the virgin
season, so the arm could never be dev-tested (F7 — dropped at the
feature step, BR precedent).
Forbidden: as G-NO plus defensive xGOT (R5), two-stage generative
distributions (V11 stands).

## 3. C-NO — corners
Reference: `model_corners_v3` via the J1 engine `corners/` (ratings +
NB total + territorial multiplier). **Primary line 10.5** for this
league (dev mean 10.55 corners; the AU-ALeague precedent — its corners
primary was also 10.5 — retargets the reference's fit-loss line and
ladder, nothing else in the pattern changes).
Arms: **Gate Zero** (X9 covariates: possession + big chances);
**X7** — box-touch multiplier (X7, F9: trait r=0.935/0.766, corr 0.600
vs possession 0.449), constructed as C-J1's X7 arm with the min-8
trailing rule absorbing the pre-2024 coverage ramp (arm falls back to
Gate Zero where its window is thin).

## 4. K-NO — cards (yellows)
Reference: `model_cards.py` via the J1 engine `cards/` (team card
ratings, count distribution; referee not used in production).
Target: unified yellows (event feed, 100% coverage — Phase 2
rule 7 as amended; the stats feed undercounts in this league).
Primary line 2.5 (dev mean 3.14 event yellows, dev over-rate 62.2%;
J1's primary was also 2.5 at a 2.34 mean — the line follows this
league's dev distribution, per the template).
Arms: **Gate Zero**; **X8** — referee covariate (X8, F8 r=0.316 on
the corrected target; coverage 100% in the virgin season). Binding
conditions as K-J1: must beat Gate Zero on dev; fixtures without a
named referee fall back to the base arm (no imputation). Amendment
record: the first design pass dropped X8 on a stats-feed trait
reading (r=0.291) taken before the cards-feed audit; on the
corrected target the trait passes and the arm is restored — see
FEATURES X8 and the PREREG_K_NO amendment header.

## 5. T-NO — total shots
Reference: the shots family via the J1 engine `total_shots/`.
**Primary line 26.5** (dev mean 26.36; dispersion 1.54, the highest
of any NO market — the trailing-r question is live here).
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
